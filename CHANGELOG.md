# Changelog

## 0.4.2

- Fixed the sidebar and the changelist filter panel "blinking" on every
  page load. They were painted open and only collapsed by the deferred
  scripts, with a width transition that re-laid out the results table on
  every frame. `admin/nav_sidebar.html` now includes
  `admin_home/_preload_head.html` before the sidebar and
  `admin_home/_preload.html` as its last child, two small inline scripts that restore the saved state before the first paint and
  keep transitions off until the page has loaded. No change is needed in the host project; under a CSP without
  `'unsafe-inline'` the snippet is blocked and the previous behaviour stays.
- The changelist filter panel now sits flush against the right edge of the
  page (Django's `#content` right padding is dropped when the changelist has
  filters, on screens wider than a phone).
- On phones the collapsed filter panel is a floating button in the
  bottom-right corner (the whole pill toggles it) and the open panel is a
  drawer over the page. The 64px full-height strip covered the right edge of
  the content and its funnel was hidden behind the header.
- `hscroll.js` no longer forces a layout of the results table on every
  scroll event: reads and writes are batched into one animation frame, and
  styles are only written when they change. The bar/table scroll sync no
  longer relies on a flag that could swallow a scroll.
- `nav.js` and `filter_panel.js` put the favorite key, icon and i18n labels
  in through the DOM API instead of concatenating them into HTML, and the
  favorite card no longer uses an inline `onclick`.

## 0.4.1

- Added the `ADMIN_HOME_SHOW_WELCOME_BANNER` setting (default `True`) to
  hide the "Hello, <name>" banner at the top of the home page.
- Fixed a stray line at one tip of the changelist filter chevron. Django's
  `changelists.css`, which loads after `filter_panel.css`, puts its own
  `→`/`↓` glyph in the same `summary::before`, and the glyph leaked out of
  the rotated chevron box.

## 0.4.0

- Declared support for Django 3.2 through 6.0 and Python 3.10 or newer.
  Added a tox matrix for each supported Django/Python combination. Python
  3.15 remains unbounded at package level and will enter the matrix when a
  Django release officially supports it.

## 0.3.0

- Added two optional, settings-free extras: a collapsible changelist
  filter panel (`filter_panel.css`/`.js`) and a floating horizontal
  scrollbar for wide results tables (`hscroll.css`/`.js`). Both only
  rewrite Django's own native markup (`#changelist-filter`,
  `#changelist-form .results`), reuse the existing `--admin-home-nav-*`
  theme tokens (so dark mode just works), and need no Python wiring —
  just include the CSS/JS. Labels default to English, translatable via
  `window.ADMIN_HOME_I18N` (same pattern as the home dashboard's
  "Favorites" label). Added the `i-filter` icon to the bundled sprite.
  Each filter facet (Django always renders its `<details>` open) now
  starts closed and remembers what the user opened, same rule the
  sidebar's app groups already use.

## 0.2.4

- Fixed the language flags in the user menu: `.admin-home-user-menu__flag`
  (combined with the shared `admin-home-icon` class on the same `<svg>`)
  now sets `stroke: none`. `admin-home-icon` sets `stroke: currentColor`
  + `stroke-width: 2` for line icons, which flag symbols inherited even
  though most of their shapes have no stroke of their own — on thin
  shapes (e.g. the US flag's stripes) a 2-unit-wide stroke is thicker
  than the shape itself and completely hides the fill color underneath.

## 0.2.3

- The shared `admin-home-icon` class (sidebar, home dashboard, user menu)
  now also sets `stroke-width: 2; stroke-linecap: round; stroke-linejoin:
  round`. Same root cause as the 0.2.2 fill/stroke fix: the sprite's
  `<symbol>` elements share a `<g stroke-width="2" ...>` wrapper in the
  `<defs>` for these presentation attributes, but a `<use>` instance's
  generated shadow tree does not inherit from that wrapper — only from its
  own light-DOM ancestors. Without this, every icon in the admin (not just
  the user menu) rendered with the SVG-default 1px, square-cap stroke
  instead of the intended bold 2px line-icon look.

## 0.2.2

- Fixed the user menu icons rendering as solid black shapes instead of thin
  line icons: the shared `admin-home-icon` class (which sets
  `fill: none; stroke: currentColor`) was missing from every bare `<svg>`
  in `_user_menu.html` (identity, section titles, theme buttons, footer
  actions) — without it, browsers fall back to the SVG default
  `fill: black`, which is nearly invisible on light backgrounds and a
  solid dark blob on dark ones. `nav_sidebar.html`/`index.html` always
  included this class; the user menu template didn't.
- `CUSTOM_PAGES_GROUP_NAME` ("Pages") is now wrapped in `gettext_lazy` —
  it was a plain Python string, so it could never be translated by a host
  project's own locale catalog no matter the active language.

## 0.2.1

- Fixed a contrast bug in the user menu: `<a>` actions ("Change password",
  and any host-provided extra action) could inherit an illegible color in
  dark mode from the host's own `#header a:link`/`a:visited` styling
  (Django's base admin CSS and many themes set this for the branded header
  bar, not for a popover panel nested inside `#header`). The sibling
  "Log out" `<button>` was unaffected because that selector only matches
  `<a>`. Fixed by matching the same selector specificity in
  `user_menu.css`.

## 0.2.0

- Added the admin header user menu: identity, a language switcher driven
  by `settings.LANGUAGES` (`django_admin_home.context_processors.admin_languages`),
  an explicit Auto/Light/Dark theme switcher reusing the admin's own
  `localStorage.theme`/`data-theme` contract, and account shortcuts
  (change password, log out). New optional settings
  `ADMIN_HOME_LANGUAGE_LABELS` / `ADMIN_HOME_LANGUAGE_FLAGS`. Extension
  point via `admin_home/_user_menu_extra_actions.html` template override.

## 0.1.0

- Initial extraction from a private Django project's admin customizations
  into a standalone, generic package: tree-navigation sidebar
  (`admin/nav_sidebar.html`), a home dashboard with favorites/most-accessed
  cards (`admin/index.html`), per-user `MenuFavorite`/`MenuAccess` models,
  an optional "Pages" group for custom links (`ADMIN_HOME_CUSTOM_PAGES`),
  and settings-driven icon mapping (`ADMIN_HOME_APP_ICONS` /
  `ADMIN_HOME_MODEL_ICONS`).

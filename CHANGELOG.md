# Changelog

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

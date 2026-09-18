# Changelog

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

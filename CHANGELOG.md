# Changelog

## 0.1.0

- Initial extraction from a private Django project's admin customizations
  into a standalone, generic package: tree-navigation sidebar
  (`admin/nav_sidebar.html`), a home dashboard with favorites/most-accessed
  cards (`admin/index.html`), per-user `MenuFavorite`/`MenuAccess` models,
  an optional "Pages" group for custom links (`ADMIN_HOME_CUSTOM_PAGES`),
  and settings-driven icon mapping (`ADMIN_HOME_APP_ICONS` /
  `ADMIN_HOME_MODEL_ICONS`).

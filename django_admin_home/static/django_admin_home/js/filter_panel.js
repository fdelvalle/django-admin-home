/* =====================================================================
   django-admin-home — collapsible changelist filter panel
   - Reorganizes Django's native #changelist-filter into a panel with a
     header (funnel icon + title + collapse/expand button).
   - Collapse/expand state persisted in localStorage (same idea as the
     sidebar).
   - Labels default to English; a host project can translate them by
     setting window.ADMIN_HOME_I18N.filters / .toggleFilters before this
     script runs (same pattern used for the home dashboard's "Favorites"
     label).
   ===================================================================== */
(function () {
    "use strict";

    var STORAGE_COLLAPSED = "admin-home:filter-collapsed";
    var STORAGE_FACET_PREFIX = "admin-home:filter-open:";

    function i18n(key, fallback) {
        var strings = window.ADMIN_HOME_I18N || {};
        return strings[key] || fallback;
    }

    function svg(icon, extraClass) {
        return (
            '<svg class="admin-home-icon ' + (extraClass || "") + '" aria-hidden="true">' +
            '<use href="#' + icon + '"></use></svg>'
        );
    }

    function buildHeader() {
        var header = document.createElement("div");
        header.className = "admin-home-filter-header";
        var filtersLabel = i18n("filters", "Filters");
        var toggleLabel = i18n("toggleFilters", "Collapse/expand filters");
        header.innerHTML =
            '<span class="admin-home-filter-title">' +
            svg("i-filter", "admin-home-filter-icon") +
            '<span class="admin-home-filter-title-text">' + filtersLabel + "</span>" +
            "</span>" +
            '<button class="admin-home-filter-toggle" type="button" ' +
            'aria-label="' + toggleLabel + '" title="' + toggleLabel + '">' +
            svg("i-chevron", "admin-home-filter-caret") +
            "</button>";
        return header;
    }

    function initFilterPanel() {
        var filter = document.getElementById("changelist-filter");
        if (!filter) return;

        // Defend against double injection.
        if (filter.querySelector(".admin-home-filter-header")) return;

        // Wrap the native content (h2/details/ul...) in a body, keeping the
        // header separate.
        var body = document.createElement("div");
        body.className = "admin-home-filter-body";
        while (filter.firstChild) {
            body.appendChild(filter.firstChild);
        }

        var header = buildHeader();
        filter.appendChild(header);
        filter.appendChild(body);

        // Collapsed by default; only stays open if the user explicitly
        // expanded it before (localStorage === "0").
        var startCollapsed = localStorage.getItem(STORAGE_COLLAPSED) !== "0";
        filter.classList.toggle("is-collapsed", startCollapsed);

        var toggle = header.querySelector(".admin-home-filter-toggle");
        if (toggle) {
            toggle.addEventListener("click", function () {
                var collapsed = filter.classList.toggle("is-collapsed");
                localStorage.setItem(STORAGE_COLLAPSED, collapsed ? "1" : "0");
            });
        }

        initFacets(body);
    }

    // Each filter facet (Django renders one <details data-filter-title="...">
    // per facet, always open) starts closed, independently of the others —
    // same "closed by default, remember what you opened" rule the sidebar's
    // app groups use. Keyed by page path + facet title, since the same
    // title (e.g. "By active") can mean something different on every
    // changelist.
    function facetKey(details, index) {
        var title = details.getAttribute("data-filter-title") || String(index);
        return STORAGE_FACET_PREFIX + window.location.pathname + "|" + title;
    }

    function initFacets(body) {
        var facets = body.querySelectorAll("details");
        facets.forEach(function (details, index) {
            var key = facetKey(details, index);
            details.open = localStorage.getItem(key) === "1";
            details.addEventListener("toggle", function () {
                localStorage.setItem(key, details.open ? "1" : "0");
            });
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initFilterPanel);
    } else {
        initFilterPanel();
    }
})();

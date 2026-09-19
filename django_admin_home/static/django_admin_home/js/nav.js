/* =====================================================================
   django-admin-home — sidebar navigation + home dashboard
   - Collapse/expand sidebar (persisted in localStorage)
   - Collapse app groups
   - Favorite items (star) via AJAX
   - Track menu accesses (counter) via AJAX
   ===================================================================== */
(function () {
    "use strict";

    var STORAGE_COLLAPSED = "admin-home:nav-collapsed";
    var MOBILE_BREAKPOINT = "(max-width: 767px)";

    function getCookie(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length === 2) return parts.pop().split(";").shift();
        return null;
    }

    function csrfToken() {
        return getCookie("csrftoken") || "";
    }

    function post(url, params) {
        var body = new URLSearchParams(params);
        return fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken(),
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest"
            },
            credentials: "same-origin",
            body: body.toString()
        });
    }

    /* ---------- Collapse / expand sidebar ---------- */
    function initSidebarToggle() {
        var sidebar = document.getElementById("admin-home-sidebar");
        var toggle = document.getElementById("admin-home-nav-toggle");
        if (!sidebar) return;

        var media = window.matchMedia(MOBILE_BREAKPOINT);

        function applyViewportState() {
            // The navigation is an off-canvas overlay on phones. Always start
            // it closed there, regardless of the desktop preference saved in
            // localStorage. Returning to a larger screen restores that choice.
            var collapsed = media.matches || localStorage.getItem(STORAGE_COLLAPSED) === "1";
            sidebar.classList.toggle("is-collapsed", collapsed);
        }

        applyViewportState();
        media.addEventListener("change", applyViewportState);

        if (toggle) {
            toggle.addEventListener("click", function () {
                var collapsed = sidebar.classList.toggle("is-collapsed");
                // Mobile is intentionally transient: it opens the drawer for
                // this page only and never changes the desktop preference.
                if (!media.matches) {
                    localStorage.setItem(STORAGE_COLLAPSED, collapsed ? "1" : "0");
                }
            });
        }
    }

    /* ---------- Group state (persisted per browser) ----------
       Key per group: "admin-home:nav-group:<appKey>" = "open" | "closed".
       Default (no saved value): COLLAPSED. */
    var GROUP_PREFIX = "admin-home:nav-group:";

    function groupKey(group) {
        return group.getAttribute("data-app") || "";
    }

    function setGroupState(group, open, persist) {
        group.setAttribute("aria-collapsed", open ? "false" : "true");
        var header = group.querySelector(".admin-home-nav-group-header");
        if (header) header.setAttribute("aria-expanded", open ? "true" : "false");
        if (persist) {
            var key = groupKey(group);
            if (key) localStorage.setItem(GROUP_PREFIX + key, open ? "open" : "closed");
        }
    }

    /* ---------- Active item (current route) ---------- */
    function initActiveItem() {
        var path = window.location.pathname;
        var best = null, bestLen = -1;
        document.querySelectorAll(".admin-home-nav-item[data-url]").forEach(function (item) {
            var url = item.getAttribute("data-url");
            if (!url) return;
            // Marks the item whose URL is the longest prefix of the current route.
            if (path === url || path.indexOf(url) === 0) {
                if (url.length > bestLen) { best = item; bestLen = url.length; }
            }
        });
        if (best) {
            best.classList.add("is-active");
            var group = best.closest(".admin-home-nav-group");
            if (group) setGroupState(group, true, true);
        }
    }

    /* ---------- Collapse app groups ---------- */
    function initGroups() {
        document.querySelectorAll(".admin-home-nav-group").forEach(function (group) {
            var key = groupKey(group);
            var saved = key ? localStorage.getItem(GROUP_PREFIX + key) : null;
            setGroupState(group, saved === "open", false);
        });

        document.querySelectorAll(".admin-home-nav-group-header").forEach(function (header) {
            header.addEventListener("click", function () {
                var group = header.closest(".admin-home-nav-group");
                if (!group) return;
                var open = group.getAttribute("aria-collapsed") === "true"; // will open
                setGroupState(group, open, true);
            });
        });
    }

    /* ---------- Favorite (star) ---------- */
    function favoriteUrl() {
        var el = document.querySelector("[data-toggle-favorite-url]");
        return el ? el.getAttribute("data-toggle-favorite-url") : null;
    }

    function syncStars(menuKey, isFavorite) {
        document.querySelectorAll('.admin-home-star[data-menu-key="' + cssEscape(menuKey) + '"]').forEach(function (star) {
            star.classList.toggle("is-favorite", isFavorite);
            star.setAttribute("aria-pressed", isFavorite ? "true" : "false");
        });
    }

    /* ---------- Immediate update of the home "Favorites" section ----------
       On (un)favorite, reflect the change instantly, without a reload:
       - removed: drops the card from the grid; if empty, removes the section.
       - added: inserts the card (creating the section if missing), reusing
         name/icon/parent from the item that originated the click. */

    function homeFavoritesGrid() {
        var section = document.querySelector(".admin-home-favorites-section");
        return section ? section.querySelector(".admin-home-card-grid") : null;
    }

    function removeHomeFavoriteCard(menuKey) {
        var grid = homeFavoritesGrid();
        if (!grid) return;
        var card = grid.querySelector('.admin-home-card[data-menu-key="' + cssEscape(menuKey) + '"]');
        if (card) card.remove();
        if (!grid.querySelector(".admin-home-card")) {
            var section = grid.closest(".admin-home-favorites-section");
            if (section) section.remove();
        }
    }

    function iconIdFromStar(sourceEl) {
        if (!sourceEl) return "grid";
        var item = sourceEl.closest(".admin-home-nav-item, .admin-home-card") || sourceEl.parentNode;
        var use = item ? item.querySelector(".admin-home-nav-icon .admin-home-icon use, .admin-home-card-icon .admin-home-icon use") : null;
        var href = use ? (use.getAttribute("href") || use.getAttribute("xlink:href") || "") : "";
        var m = href.match(/#i-(.+)$/);
        return m ? m[1] : "grid";
    }

    function metaFromStar(sourceEl, menuKey) {
        var item = sourceEl ? sourceEl.closest(".admin-home-nav-item, .admin-home-card") : null;
        var link = item ? item.querySelector("a[data-menu-key]") : null;
        var name = "";
        if (link) {
            var label = link.querySelector(".admin-home-nav-label, .admin-home-card-name");
            name = (label ? label.textContent : link.textContent) || "";
        }
        return {
            key: menuKey,
            name: name.trim() || menuKey,
            url: link ? link.getAttribute("href") : "#",
            icon: iconIdFromStar(sourceEl),
            newTab: !!(link && link.getAttribute("target") === "_blank")
        };
    }

    function buildFavoriteCard(meta) {
        var a = document.createElement("a");
        a.className = "admin-home-card admin-home-card--fav";
        a.href = meta.url || "#";
        a.setAttribute("data-menu-key", meta.key);
        if (meta.newTab) { a.target = "_blank"; a.rel = "noopener"; }

        a.innerHTML =
            '<span class="admin-home-card-icon"><svg class="admin-home-icon" aria-hidden="true">' +
            '<use href="#i-' + meta.icon + '"></use></svg></span>' +
            '<span class="admin-home-card-body"><span class="admin-home-card-name"></span></span>' +
            '<button class="admin-home-star is-favorite" type="button" data-menu-key="' + meta.key + '" ' +
            'aria-pressed="true" onclick="event.preventDefault();event.stopPropagation();">' +
            '<svg class="admin-home-icon admin-home-star-on" aria-hidden="true"><use href="#i-star-filled"></use></svg>' +
            '<svg class="admin-home-icon admin-home-star-off" aria-hidden="true"><use href="#i-star"></use></svg>' +
            '</button>';
        a.querySelector(".admin-home-card-name").textContent = meta.name;
        return a;
    }

    function createHomeFavoritesSection() {
        var wrap = document.querySelector(".admin-home-wrap");
        if (!wrap) return null;
        var hero = wrap.querySelector(".admin-home-hero");

        var section = document.createElement("section");
        section.className = "admin-home-section admin-home-favorites-section";
        section.innerHTML =
            '<h2 class="admin-home-section-title">' +
            '<svg class="admin-home-icon" aria-hidden="true"><use href="#i-star-filled"></use></svg>' +
            (window.ADMIN_HOME_I18N && window.ADMIN_HOME_I18N.favorites ? window.ADMIN_HOME_I18N.favorites : "Favorites") +
            '</h2><div class="admin-home-card-grid"></div>';

        if (hero && hero.nextSibling) {
            wrap.insertBefore(section, hero.nextSibling);
        } else {
            wrap.insertBefore(section, wrap.firstChild);
        }
        return section.querySelector(".admin-home-card-grid");
    }

    function addHomeFavoriteCard(menuKey, sourceEl) {
        if (!document.querySelector(".admin-home-wrap")) return;
        var grid = homeFavoritesGrid() || createHomeFavoritesSection();
        if (!grid) return;
        if (grid.querySelector('.admin-home-card[data-menu-key="' + cssEscape(menuKey) + '"]')) return;
        grid.appendChild(buildFavoriteCard(metaFromStar(sourceEl, menuKey)));
    }

    function updateHomeFavorites(menuKey, isFavorite, sourceEl) {
        try {
            if (isFavorite) {
                addHomeFavoriteCard(menuKey, sourceEl);
            } else {
                removeHomeFavoriteCard(menuKey);
            }
        } catch (e) { /* additive: must never break the home page */ }
    }

    function cssEscape(value) {
        if (window.CSS && CSS.escape) return CSS.escape(value);
        return String(value).replace(/["\\]/g, "\\$&");
    }

    function initStars() {
        var url = favoriteUrl();
        if (!url) return;

        document.body.addEventListener("click", function (evt) {
            var star = evt.target.closest(".admin-home-star");
            if (!star) return;
            evt.preventDefault();
            evt.stopPropagation();

            var menuKey = star.getAttribute("data-menu-key");
            if (!menuKey || star.classList.contains("is-busy")) return;

            star.classList.add("is-busy");
            post(url, { menu_key: menuKey })
                .then(function (r) { return r.ok ? r.json() : Promise.reject(r); })
                .then(function (data) {
                    var isFav = !!data.is_favorite;
                    // Update the home page BEFORE syncing stars, since removing
                    // the card also removes the `star` that originated the click.
                    updateHomeFavorites(menuKey, isFav, star);
                    syncStars(menuKey, isFav);
                })
                .catch(function () { /* silent: favoriting is additive */ })
                .finally(function () { if (star.isConnected) star.classList.remove("is-busy"); });
        });
    }

    /* ---------- Track menu access ---------- */
    function trackUrl() {
        var el = document.querySelector("[data-track-access-url]");
        return el ? el.getAttribute("data-track-access-url") : null;
    }

    function initAccessTracking() {
        var url = trackUrl();
        if (!url) return;

        document.body.addEventListener("click", function (evt) {
            var link = evt.target.closest("a[data-menu-key]");
            if (!link) return;
            var menuKey = link.getAttribute("data-menu-key");
            if (!menuKey || menuKey === "home") return;

            // sendBeacon is ideal so it never delays navigation.
            var sent = false;
            if (navigator.sendBeacon) {
                var fd = new FormData();
                fd.append("menu_key", menuKey);
                fd.append("csrfmiddlewaretoken", csrfToken());
                try { sent = navigator.sendBeacon(url, fd); } catch (e) { sent = false; }
            }
            if (!sent) {
                post(url, { menu_key: menuKey });
            }
        });
    }

    /* ---------- Masonry layout toggle (pill on/off) ----------
       Persisted in localStorage: "admin-home:home-masonry" = "1" | "0". */
    var STORAGE_MASONRY = "admin-home:home-masonry";

    function initMasonryToggle() {
        var modules = document.getElementById("admin-home-modules");
        var pill = document.getElementById("admin-home-masonry-toggle");
        if (!modules || !pill) return;

        function apply(on) {
            modules.classList.toggle("is-masonry", on);
            pill.setAttribute("aria-checked", on ? "true" : "false");
        }

        apply(localStorage.getItem(STORAGE_MASONRY) === "1");

        pill.addEventListener("click", function () {
            var on = !modules.classList.contains("is-masonry");
            apply(on);
            localStorage.setItem(STORAGE_MASONRY, on ? "1" : "0");
        });
    }

    function init() {
        initSidebarToggle();
        initGroups();       // restores saved state (default: collapsed)
        initActiveItem();   // then opens the group of the active route
        initStars();
        initAccessTracking();
        initMasonryToggle();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();

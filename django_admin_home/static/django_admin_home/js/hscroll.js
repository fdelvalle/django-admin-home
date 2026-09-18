/* =====================================================================
   django-admin-home — floating horizontal scrollbar
   Creates a bar fixed to the bottom of the viewport, synced with the
   results table's (#changelist-form .results) horizontal scroll, so the
   table can be scrolled sideways without reaching its own end first.

   - Only shows up when the table is wider than its visible area.
   - Syncs scroll both ways (bar <-> table).
   - Reacts to window resize and width changes (ResizeObserver).
   - Hides itself when the table's own native scrollbar is already
     visible on screen (avoids two overlapping bars at the table's end).
   ===================================================================== */
(function () {
    "use strict";

    function initHScroll() {
        var results = document.querySelector("#changelist-form .results");
        if (!results) return;

        var table = results.querySelector("table");
        if (!table) return;

        var bar = document.createElement("div");
        bar.className = "admin-home-hscroll";
        bar.setAttribute("aria-hidden", "true");
        bar.hidden = true;

        var track = document.createElement("div");
        track.className = "admin-home-hscroll-track";
        bar.appendChild(track);
        document.body.appendChild(bar);
        document.body.classList.add("admin-home-has-hscroll");

        var syncing = false;

        function positionBar() {
            var rect = results.getBoundingClientRect();
            bar.style.left = rect.left + "px";
            bar.style.width = rect.width + "px";
        }

        function refresh() {
            positionBar();
            track.style.width = table.scrollWidth + "px";

            var hasOverflow = table.scrollWidth > results.clientWidth + 1;
            if (!hasOverflow) {
                bar.hidden = true;
                return;
            }

            // If the table's own end (where the native scrollbar lives) is
            // already visible in the viewport, skip the floating bar.
            var rect = results.getBoundingClientRect();
            var nativeVisible = rect.bottom <= window.innerHeight + 1;
            bar.hidden = nativeVisible;

            if (!bar.hidden) bar.scrollLeft = results.scrollLeft;
        }

        bar.addEventListener("scroll", function () {
            if (syncing) { syncing = false; return; }
            syncing = true;
            results.scrollLeft = bar.scrollLeft;
        });
        results.addEventListener("scroll", function () {
            if (!bar.hidden) {
                if (syncing) { syncing = false; return; }
                syncing = true;
                bar.scrollLeft = results.scrollLeft;
            }
        });

        window.addEventListener("resize", refresh);
        window.addEventListener("scroll", refresh, { passive: true });

        if (window.ResizeObserver) {
            var ro = new ResizeObserver(refresh);
            ro.observe(table);
            ro.observe(results);
        }

        // Recompute once layout settles (fonts/images/reflow).
        refresh();
        window.setTimeout(refresh, 250);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initHScroll);
    } else {
        initHScroll();
    }
})();

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

        var frame = 0;
        var last = {};

        function setStyle(el, prop, value) {
            var key = el === bar ? "bar." + prop : "track." + prop;
            if (last[key] === value) return;
            last[key] = value;
            el.style[prop] = value;
        }

        // Reads everything first, then writes: interleaving them (as the
        // first version did, on every scroll event) forced a synchronous
        // layout of the whole results table each time.
        function refresh() {
            frame = 0;
            var rect = results.getBoundingClientRect();
            var scrollWidth = table.scrollWidth;
            var hasOverflow = scrollWidth > results.clientWidth + 1;
            // If the table's own end (where the native scrollbar lives) is
            // already visible in the viewport, skip the floating bar.
            var nativeVisible = rect.bottom <= window.innerHeight + 1;
            var scrollLeft = results.scrollLeft;

            setStyle(bar, "left", rect.left + "px");
            setStyle(bar, "width", rect.width + "px");
            setStyle(track, "width", scrollWidth + "px");

            var hidden = !hasOverflow || nativeVisible;
            if (bar.hidden !== hidden) bar.hidden = hidden;
            if (!hidden && bar.scrollLeft !== scrollLeft) bar.scrollLeft = scrollLeft;
        }

        // Scroll/resize/ResizeObserver can fire many times per frame (and on
        // every frame of a sidebar/filter animation): coalesce into one.
        function schedule() {
            if (!frame) frame = window.requestAnimationFrame(refresh);
        }

        // Copy only when the values differ: assigning an unchanged
        // scrollLeft fires no event, so this can't ping-pong (a boolean
        // "syncing" flag could get stuck and swallow the next scroll).
        bar.addEventListener("scroll", function () {
            if (results.scrollLeft !== bar.scrollLeft) results.scrollLeft = bar.scrollLeft;
        });
        results.addEventListener("scroll", function () {
            if (!bar.hidden && bar.scrollLeft !== results.scrollLeft) bar.scrollLeft = results.scrollLeft;
        });

        window.addEventListener("resize", schedule);
        window.addEventListener("scroll", schedule, { passive: true });

        if (window.ResizeObserver) {
            var ro = new ResizeObserver(schedule);
            ro.observe(table);
            ro.observe(results);
        }

        // Recompute once layout settles (fonts/images/reflow).
        refresh();
        window.setTimeout(schedule, 250);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initHScroll);
    } else {
        initHScroll();
    }
})();

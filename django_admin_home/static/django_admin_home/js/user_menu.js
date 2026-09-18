'use strict';
/*
 * Admin header user menu.
 *
 * Responsibilities:
 *   - open/close the panel (click, Esc, click outside, focus leaving);
 *   - arrow-key navigation between items;
 *   - apply the theme choice (Auto/Light/Dark).
 *
 * About the theme: the Django admin's own native `theme.js` keeps `setTheme`
 * inside a closure, so it can't be called from here. What IS public is the
 * *contract* it reads on boot — `localStorage.theme` + `data-theme` on
 * `<html>` — and that's exactly what we replicate below. Changing the theme
 * from here still holds after a reload, without touching Django's file.
 */
{
    const VALID_THEMES = ['auto', 'light', 'dark'];

    function applyTheme(mode) {
        const theme = VALID_THEMES.includes(mode) ? mode : 'auto';
        document.documentElement.dataset.theme = theme;
        try {
            localStorage.setItem('theme', theme);
        } catch (e) {
            // Private mode / storage blocked: the theme only holds for this page.
        }
        return theme;
    }

    function currentTheme() {
        try {
            return localStorage.getItem('theme') || 'auto';
        } catch (e) {
            return document.documentElement.dataset.theme || 'auto';
        }
    }

    function initMenu(root) {
        const trigger = root.querySelector('.admin-home-user-menu__trigger');
        const panel = root.querySelector('.admin-home-user-menu__panel');
        if (!trigger || !panel) {
            return;
        }

        function focusableItems() {
            return Array.from(
                panel.querySelectorAll('a[href], button:not([disabled])')
            ).filter(function (el) {
                return el.offsetParent !== null;
            });
        }

        function isOpen() {
            return trigger.getAttribute('aria-expanded') === 'true';
        }

        function open() {
            panel.hidden = false;
            trigger.setAttribute('aria-expanded', 'true');
        }

        function close(returnFocus) {
            panel.hidden = true;
            trigger.setAttribute('aria-expanded', 'false');
            if (returnFocus) {
                trigger.focus();
            }
        }

        trigger.addEventListener('click', function (event) {
            event.stopPropagation();
            if (isOpen()) {
                close(false);
            } else {
                open();
            }
        });

        // A click outside closes it. The listener lives on `document` and
        // checks containment, rather than blur, so clicks inside the panel
        // itself don't close it.
        document.addEventListener('click', function (event) {
            if (isOpen() && !root.contains(event.target)) {
                close(false);
            }
        });

        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && isOpen()) {
                close(true);
            }
        });

        // Arrows navigate items; Home/End jump to the ends.
        panel.addEventListener('keydown', function (event) {
            const items = focusableItems();
            if (!items.length) {
                return;
            }
            const index = items.indexOf(document.activeElement);

            if (event.key === 'ArrowDown') {
                event.preventDefault();
                items[(index + 1) % items.length].focus();
            } else if (event.key === 'ArrowUp') {
                event.preventDefault();
                items[(index - 1 + items.length) % items.length].focus();
            } else if (event.key === 'Home') {
                event.preventDefault();
                items[0].focus();
            } else if (event.key === 'End') {
                event.preventDefault();
                items[items.length - 1].focus();
            }
        });

        // Down-arrow on the trigger opens the menu straight into the first item.
        trigger.addEventListener('keydown', function (event) {
            if (event.key === 'ArrowDown') {
                event.preventDefault();
                open();
                const items = focusableItems();
                if (items.length) {
                    items[0].focus();
                }
            }
        });

        initThemeButtons(panel);
    }

    function initThemeButtons(panel) {
        const buttons = Array.from(panel.querySelectorAll('[data-theme-value]'));
        if (!buttons.length) {
            return;
        }

        function sync(active) {
            buttons.forEach(function (btn) {
                const pressed = btn.dataset.themeValue === active;
                btn.setAttribute('aria-pressed', pressed ? 'true' : 'false');
            });
        }

        buttons.forEach(function (btn) {
            btn.addEventListener('click', function () {
                sync(applyTheme(btn.dataset.themeValue));
            });
        });

        sync(currentTheme());
    }

    function init() {
        document.querySelectorAll('[data-admin-home-user-menu]').forEach(initMenu);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
}

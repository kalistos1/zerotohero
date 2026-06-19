/**
 * 1. Immediate Execution Function
 * Prevents the "white flash" by setting the theme before the page body renders.
 */
!function() {
    const savedThemeConfig = sessionStorage.getItem("__THEME_CONFIG__");
    const htmlElement = document.documentElement;
    const defaultTheme = { theme: "light" };
    let currentConfig;

    // Check for saved config, otherwise check HTML attribute
    if (savedThemeConfig) {
        currentConfig = JSON.parse(savedThemeConfig);
    } else {
        const attrTheme = htmlElement.getAttribute("data-bs-theme");
        currentConfig = { theme: attrTheme || defaultTheme.theme };
    }

    // Set global variables for the Class to use later
    window.config = currentConfig;
    window.defaultConfig = JSON.parse(JSON.stringify(currentConfig));

    // Apply immediately to HTML tag
    htmlElement.setAttribute("data-bs-theme", currentConfig.theme);
}();

/**
 * 2. ThemeCustomizer Class
 * Handles UI updates, button toggles, and event listeners.
 */
class ThemeCustomizer {
    constructor() {
        this.html = document.documentElement;
        this.config = window.config;
    }

    init() {
        this.initConfig();
        this.initListeners();
    }

    initConfig() {
        // Sync everything on startup
        this.applyTheme(this.config.theme);
    }

    applyTheme(theme) {
        this.config.theme = theme;
        this.html.setAttribute("data-bs-theme", theme);
        
        // Save to Session Storage
        sessionStorage.setItem("__THEME_CONFIG__", JSON.stringify(this.config));
        sessionStorage.setItem("__THEME_LABEL__", theme === "dark" ? "Dark" : "Light");

        // --- FIXED: Handle the two-button toggle (.moon and .sun) ---
        const moonBtn = document.querySelector('.theme-toggle.moon');
        const sunBtn = document.querySelector('.theme-toggle.sun');

        if (theme === "dark") {
            if (moonBtn) moonBtn.classList.add('activate');
            if (sunBtn) sunBtn.classList.remove('activate');
        } else {
            if (sunBtn) sunBtn.classList.add('activate');
            if (moonBtn) moonBtn.classList.remove('activate');
        }

        // --- FIXED: Handle generic toggle buttons (.light-dark-mode) ---
        const generalToggles = document.querySelectorAll(".light-dark-mode");
        generalToggles.forEach(btn => {
            if (theme === "dark") {
                btn.classList.add('mode-dark');
                btn.classList.remove('mode-light');
            } else {
                btn.classList.add('mode-light');
                btn.classList.remove('mode-dark');
            }
        });

        // Sync Radio Buttons (Settings Sidebar)
        const radio = document.querySelector(`input[name=data-bs-theme][value="${theme}"]`);
        if (radio) radio.checked = true;

        // Sync Dropdown Text
        const dropdownToggle = document.querySelector(".theme-dropdown .dropdown-toggle");
        if (dropdownToggle) dropdownToggle.textContent = theme.charAt(0).toUpperCase() + theme.slice(1);
    }

    initListeners() {
        const self = this;

        // 1. Separate Moon/Sun button listeners
        const moonBtn = document.querySelector('.theme-toggle.moon');
        if (moonBtn) {
            moonBtn.addEventListener('click', () => self.applyTheme('dark'));
        }

        const sunBtn = document.querySelector('.theme-toggle.sun');
        if (sunBtn) {
            sunBtn.addEventListener('click', () => self.applyTheme('light'));
        }

        // 2. Generic toggle button listeners (.light-dark-mode)
        document.querySelectorAll(".light-dark-mode").forEach(btn => {
            btn.addEventListener("click", () => {
                const targetTheme = self.config.theme === "light" ? "dark" : "light";
                self.applyTheme(targetTheme);
            });
        });

        // 3. Settings Sidebar Radio buttons
        document.querySelectorAll("input[name=data-bs-theme]").forEach(radio => {
            radio.addEventListener("change", (e) => self.applyTheme(e.target.value));
        });

        // 4. Dropdown Menu Items
        const lightDrop = document.querySelector(".dropdown-item.light-mode");
        const darkDrop = document.querySelector(".dropdown-item.dark-mode");
        if (lightDrop) lightDrop.addEventListener("click", () => self.applyTheme("light"));
        if (darkDrop) darkDrop.addEventListener("click", () => self.applyTheme("dark"));
    }
}

// 3. Initialize Class when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    const customizer = new ThemeCustomizer();
    customizer.init();
});
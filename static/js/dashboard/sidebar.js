document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.querySelector(".dashboard-sidebar");
    const overlay = document.querySelector(".sidebar-overlay");
    const toggleButtons = document.querySelectorAll(
        "[data-sidebar-toggle], .sidebar-toggle, #sidebarToggle"
    );
    const closeButtons = document.querySelectorAll(
        "[data-sidebar-close], .sidebar-close, #sidebarClose"
    );

    function openSidebar() {
        if (sidebar) sidebar.classList.add("show");
        if (overlay) overlay.classList.add("show");
        document.body.classList.add("sidebar-open");
    }

    function closeSidebar() {
        if (sidebar) sidebar.classList.remove("show");
        if (overlay) overlay.classList.remove("show");
        document.body.classList.remove("sidebar-open");
    }

    toggleButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            if (sidebar && sidebar.classList.contains("show")) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
    });

    closeButtons.forEach(function (button) {
        button.addEventListener("click", closeSidebar);
    });

    if (overlay) {
        overlay.addEventListener("click", closeSidebar);
    }

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeSidebar();
        }
    });
});
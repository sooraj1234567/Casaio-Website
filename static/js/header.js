// User Profile Dropdown Toggle
document.addEventListener('DOMContentLoaded', function () {

    const userProfileToggle = document.getElementById('userProfileToggle');
    const userDropdownMenu = document.getElementById('userDropdownMenu');

    if (!userProfileToggle || !userDropdownMenu) return;

    userProfileToggle.addEventListener('click', function (e) {

        e.stopPropagation();
        const isOpen = userDropdownMenu.classList.toggle('show');
        userProfileToggle.setAttribute('aria-expanded', String(isOpen));

    });

    userDropdownMenu.querySelectorAll('.dropdown-item').forEach(item => {

        item.addEventListener('click', function () {

            userDropdownMenu.classList.remove('show');
            userProfileToggle.setAttribute('aria-expanded', 'false');

        });

    });

    document.addEventListener('click', function (e) {

        if (!e.target.closest('.user-profile-dropdown')) {

            userDropdownMenu.classList.remove('show');
            userProfileToggle.setAttribute('aria-expanded', 'false');

        }

    });

    document.addEventListener('keydown', function (e) {

        if (e.key === 'Escape') {

            userDropdownMenu.classList.remove('show');
            userProfileToggle.setAttribute('aria-expanded', 'false');

        }

    });

});
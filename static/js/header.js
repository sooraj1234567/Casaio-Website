// User Profile Dropdown Toggle
document.addEventListener('DOMContentLoaded', function () {

    const userProfileToggle = document.getElementById('userProfileToggle');
    const userDropdownMenu = document.getElementById('userDropdownMenu');

    if (!userProfileToggle || !userDropdownMenu) return;

    userProfileToggle.addEventListener('click', function (e) {

        e.stopPropagation();
        userDropdownMenu.classList.toggle('active');

    });

    userDropdownMenu.querySelectorAll('.dropdown-item').forEach(item => {

        item.addEventListener('click', function () {

            userDropdownMenu.classList.remove('active');

        });

    });

    document.addEventListener('click', function (e) {

        if (!e.target.closest('.user-profile-dropdown')) {

            userDropdownMenu.classList.remove('active');

        }

    });

    document.addEventListener('keydown', function (e) {

        if (e.key === 'Escape') {

            userDropdownMenu.classList.remove('active');

        }

    });

});
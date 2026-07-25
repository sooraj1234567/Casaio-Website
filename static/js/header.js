// User Profile Dropdown Toggle
document.addEventListener('DOMContentLoaded', function() {
	const userProfileToggle = document.getElementById('userProfileToggle');
	const userDropdownMenu = document.getElementById('userDropdownMenu');

	if (!userProfileToggle || !userDropdownMenu) return;

	// Toggle dropdown on button click
	userProfileToggle.addEventListener('click', function(e) {
		e.stopPropagation();
		userDropdownMenu.classList.toggle('active');
	});

	// Close dropdown when clicking on a link
	const dropdownItems = userDropdownMenu.querySelectorAll('.dropdown-item');
	dropdownItems.forEach(item => {
		item.addEventListener('click', function() {
			userDropdownMenu.classList.remove('active');
		});
	});

	// Close dropdown when clicking outside
	document.addEventListener('click', function(e) {
		if (!e.target.closest('.user-profile-dropdown')) {
			userDropdownMenu.classList.remove('active');
		}
	});

	// Close dropdown on Escape key
	document.addEventListener('keydown', function(e) {
		if (e.key === 'Escape') {
			userDropdownMenu.classList.remove('active');
		}
	});
});

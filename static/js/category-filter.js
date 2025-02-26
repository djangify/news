// static/js/category-filter.js
document.addEventListener('DOMContentLoaded', function () {
  const filterToggle = document.getElementById('filter-toggle');
  const categoriesGrid = document.getElementById('categories-grid');
  const filterIcon = document.getElementById('filterIcon');

  if (filterToggle && categoriesGrid && filterIcon) {
    filterToggle.addEventListener('click', function () {
      categoriesGrid.classList.toggle('hidden');
      // Rotate the arrow icon
      filterIcon.style.transform = categoriesGrid.classList.contains('hidden') ? 'rotate(0deg)' : 'rotate(180deg)';
    });

    // Show grid by default on larger screens
    function handleResize() {
      if (window.innerWidth >= 1024) { // lg breakpoint
        categoriesGrid.classList.remove('hidden');
        filterIcon.style.transform = 'rotate(180deg)';
      } else {
        categoriesGrid.classList.add('hidden');
        filterIcon.style.transform = 'rotate(0deg)';
      }
    }

    // Initial check and listen for window resizes
    handleResize();
    window.addEventListener('resize', handleResize);
  }
});
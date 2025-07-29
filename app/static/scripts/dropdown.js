document.addEventListener("DOMContentLoaded", function () {
  const seasonBlocks = document.querySelectorAll(".season-block");
  let currentOpenDropdown = null;

  seasonBlocks.forEach((block) => {
    const dropdown = block.querySelector(".dropdown-eps");

    block.addEventListener("mouseenter", function () {
      // Close any previously open dropdown
      if (currentOpenDropdown && currentOpenDropdown !== dropdown) {
        currentOpenDropdown.style.display = "none";
        currentOpenDropdown.style.position = "fixed"; // Reset to fixed
      }

      // Show current dropdown
      dropdown.style.display = "block";
      dropdown.style.position = "relative"; // Change to relative
      dropdown.style.left = "auto";
      dropdown.style.top = "auto";
      dropdown.style.width = "100%";

      currentOpenDropdown = dropdown;
    });
  });

  // Close dropdown when leaving the entire seasons grid
  const seasonsGrid = document.querySelector(".seasons-button-grid");
  if (seasonsGrid) {
    seasonsGrid.addEventListener("mouseleave", function () {
      if (currentOpenDropdown) {
        currentOpenDropdown.style.display = "none";
        currentOpenDropdown.style.position = "fixed"; // Reset to fixed
        currentOpenDropdown = null;
      }
    });
  }
});

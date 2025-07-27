document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("comments-container");

  if (!container) return;

  // Scroll to bottom on load
  container.scrollTop = container.scrollHeight;

  // Observe attribute changes (like display: none -> block)
  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (
        mutation.type === "attributes" &&
        (mutation.attributeName === "data-hidden" || mutation.attributeName === "style")
      ) {
        const el = mutation.target;
        const isNowVisible = window.getComputedStyle(el).display !== "none";

        if (isNowVisible) {
          el.classList.add("newly-visible");
          setTimeout(() => {
            el.classList.remove("newly-visible");
          }, 1000);
        }
      }
    }

    // After all mutations processed, scroll to bottom once
    container.scrollTop = container.scrollHeight;
  });

  // Observe all comment children for attribute changes
  const comments = container.querySelectorAll(".comment");
  comments.forEach((comment) => {
    observer.observe(comment, {
      attributes: true,
      attributeFilter: ["data-hidden", "style"]
    });
  });
});

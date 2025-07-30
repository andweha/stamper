document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("showCommentsBtn");
  const commentsContainer = document.getElementById("comments-container");
  const btnText = document.getElementById("comments-btn-text");
  const arrow = document.getElementById("comments-arrow");

  let commentsVisible = localStorage.getItem("commentsVisible") === "true";

  function updateButtonUI(visible) {
    btnText.textContent = visible ? "Hide Comments" : "Show Comments";
    arrow.textContent = visible ? "⏶" : "⏷";
  }

  if (btn && commentsContainer) {
    if (commentsVisible) {
      commentsContainer.classList.remove("hidden");
    } else {
      commentsContainer.classList.add("hidden");
    }
    updateButtonUI(commentsVisible);

    btn.addEventListener("click", () => {
      commentsVisible = !commentsVisible;
      localStorage.setItem("commentsVisible", commentsVisible.toString());

      commentsContainer.classList.toggle("hidden", !commentsVisible);
      updateButtonUI(commentsVisible);
    });
  }
});


document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("comments-container");
  if (!container) return;

  let isUserAtBottom = true;

  // Check if user is near the bottom
  function checkIfAtBottom() {
    const threshold = 50; // px from bottom
    const position = container.scrollTop + container.clientHeight;
    const height = container.scrollHeight;
    isUserAtBottom = height - position < threshold;
  }

  // Scroll to bottom if user hasn't scrolled away
  function scrollToBottomIfAllowed() {
    if (isUserAtBottom) {
      container.scrollTop = container.scrollHeight;
    }
  }

  // Initial scroll on load
  container.scrollTop = container.scrollHeight;

  // Listen to manual user scroll
  container.addEventListener("scroll", checkIfAtBottom);

  // Observe comments being shown
  const observer = new MutationObserver(() => {
    scrollToBottomIfAllowed();
  });

  const comments = container.querySelectorAll(".comment-line, .comment");
  comments.forEach((comment) => {
    observer.observe(comment, { attributes: true, attributeFilter: ["data-hidden", "style"] });
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const textarea = document.querySelector(".comment-with-gif textarea");

  if (textarea) {
    const autoResize = () => {
      textarea.style.height = "auto"; // reset
      textarea.style.height = textarea.scrollHeight + "px"; // grow
    };

    textarea.addEventListener("input", autoResize);

    // Trigger resize on page load in case there's pre-filled text
    autoResize();
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector(".chat-input-form");
  const textarea = form?.querySelector("textarea");

  if (textarea && form) {
    textarea.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault(); // prevent newline
        form.requestSubmit();   // submit the form
      }
    });
  }
});

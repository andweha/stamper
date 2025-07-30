document.addEventListener("DOMContentLoaded", () => {
  const openIconButton = document.getElementById("open_gif_icon");
  const gifSearchPopup = document.getElementById("gif_search_popup");

  if (openIconButton && gifSearchPopup) {
    openIconButton.onclick = () => {
      gifSearchPopup.classList.toggle("hidden");
    };
  }

  const searchButton = document.getElementById("gif_search_btn");
  const queryInput = document.getElementById("gif_query");
  const resultsDiv = document.getElementById("gif_results");
  const previewDiv = document.getElementById("gif_preview");
  const gifUrlInput = document.getElementById("gif_url");
  const scrollWrapper = document.getElementById("gif_scroll_wrapper");

  let currentQuery = "";
  let nextPos = null;
  let isLoading = false;

  if (searchButton) {
    searchButton.onclick = async (e) => {
      e.preventDefault();
      currentQuery = queryInput.value.trim();
      if (!currentQuery) return;
      nextPos = null;
      resultsDiv.innerHTML = "";
      await fetchGifs();
    };
  }

  async function fetchGifs() {
    if (!currentQuery || isLoading) return;
    isLoading = true;

    let url = `/search_gifs?q=${encodeURIComponent(currentQuery)}`;
    if (nextPos) url += `&pos=${encodeURIComponent(nextPos)}`;

    try {
      const res = await fetch(url);
      const data = await res.json();

      data.gifs.forEach(url => {
        const wrapper = document.createElement("div");
        wrapper.className = "gif-item";

        const img = document.createElement("img");
        img.src = url;
        img.alt = "GIF";

        img.onclick = () => {
          gifUrlInput.value = url;
          gifSearchPopup.classList.add("hidden");

          // Auto-submit the form after GIF is selected
          const commentForm = document.querySelector(".chat-input-form");
          if (commentForm) {
            const submitButton = commentForm.querySelector('.comment-submit');
            if (submitButton) {
              submitButton.click();  // this avoids the shadowing issue
            } else {
              console.warn("Submit button not found.");
            }
          } else {
            console.warn("Comment form not found.");
          }
        };

        wrapper.appendChild(img);
        resultsDiv.appendChild(wrapper);
      });

      nextPos = data.next || null;
    } catch (err) {
      console.error("Error fetching GIFs:", err);
    } finally {
      isLoading = false;
    }
  }

  if (scrollWrapper) {
    scrollWrapper.addEventListener("scroll", () => {
      const { scrollTop, scrollHeight, clientHeight } = scrollWrapper;
      if (scrollTop + clientHeight >= scrollHeight - 50 && nextPos) {
        fetchGifs();
      }
    });
  }
});

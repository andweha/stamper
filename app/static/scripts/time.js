document.addEventListener("DOMContentLoaded", function () {
  const watchedElements = document.querySelectorAll(".watched-date-line");

  watchedElements.forEach(el => {
    const utc = el.dataset.watchedAt;
    if (!utc) return;

    const local = new Date(utc);
    const formatted = local.toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZoneName: 'short'
    });

    const target = el.querySelector(".local-time");
    if (target) {
      target.textContent = formatted;
    }
  });
});

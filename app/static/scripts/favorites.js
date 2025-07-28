document.querySelectorAll('.star-button').forEach(button => {
    button.addEventListener('click', async () => {
      const mediaId = button.getAttribute('data-show-id');  // Keep the attribute name for now
      const res = await fetch(`/toggle_favorite/${mediaId}`, { method: 'POST' });
      if (res.ok) {
        button.textContent = button.textContent === '⭐' ? '☆' : '⭐';
      }
    });
  });
  
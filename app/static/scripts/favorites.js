document.querySelectorAll('.star-button').forEach(button => {
    button.addEventListener('click', async (e) => {
      e.preventDefault(); // Prevent default button behavior
      e.stopPropagation(); // Prevent event from bubbling up to the parent <a> tag
      
      const mediaId = button.getAttribute('data-show-id');
      
      // Prevent multiple clicks while processing
      if (button.disabled) return;
      button.disabled = true;
      
      // Store current state
      const currentStar = button.textContent.trim();
      const newStar = currentStar === '⭐' ? '☆' : '⭐';
      
      try {
        const res = await fetch(`/toggle_favorite/${mediaId}`, { 
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          }
        });
        
        if (res.ok) {
          // Update the button text
          button.textContent = newStar;
          // Add animation class
          button.classList.add('favorited');
          setTimeout(() => button.classList.remove('favorited'), 300);
        } else {
          // If server error, keep the original state
          console.error('Server error:', res.status);
          button.textContent = currentStar;
        }
      } catch (error) {
        // If network error, keep the original state
        console.error('Network error:', error);
        button.textContent = currentStar;
      } finally {
        // Re-enable the button
        button.disabled = false;
      }
    });
  });

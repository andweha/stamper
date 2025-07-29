class ToastManager {
    constructor() {
      this.container = document.getElementById('toast-container');
      this.init();
    }
  
    init() {
      // Convert flash messages to toasts on page load
      this.convertFlashMessages();
    }
  
    convertFlashMessages() {
      const flashContainer = document.getElementById('flash-messages');
      if (!flashContainer) return;
  
      const flashMessages = flashContainer.querySelectorAll('.flash-message');
      flashMessages.forEach(flashMsg => {
        const category = flashMsg.getAttribute('data-category') || 'info';
        const message = flashMsg.textContent.trim();
        
        // Convert flash categories to toast categories
        let toastCategory = 'info';
        if (category === 'toast' || category === 'success') {
          toastCategory = 'success';
        } else if (category === 'toast-error' || category === 'danger' || category === 'error') {
          toastCategory = 'error';
        } else if (category === 'toast-warning' || category === 'warning') {
          toastCategory = 'warning';
        } else if (category === 'toast-info' || category === 'info') {
          toastCategory = 'info';
        }
        
        this.show(message, toastCategory);
      });
  
      // Remove the flash container after converting
      flashContainer.remove();
    }
  
    show(message, category = 'info', duration = 3000) {
      const toast = this.createToast(message, category, duration);
      this.container.appendChild(toast);
  
      // Trigger animation
      setTimeout(() => {
        toast.classList.add('show');
      }, 10);
  
      // Auto remove
      setTimeout(() => {
        this.remove(toast);
      }, duration);
  
      return toast;
    }
  
    createToast(message, category, duration) {
      const toast = document.createElement('div');
      toast.className = `toast ${category}`;
      
      toast.innerHTML = `
        <span class="toast-message">${this.escapeHtml(message)}</span>
        <button class="toast-close" aria-label="Close">&times;</button>
      `;
  
      // Add click to close functionality
      const closeBtn = toast.querySelector('.toast-close');
      closeBtn.addEventListener('click', () => {
        this.remove(toast);
      });
  
      // Add click on toast to close
      toast.addEventListener('click', () => {
        this.remove(toast);
      });
  
      return toast;
    }
  
    remove(toast) {
      if (!toast || !toast.parentNode) return;
  
      toast.classList.add('hide');
      
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      }, 400);
    }
  
    escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }
  
    // Public methods for manual toast creation
    success(message, duration = 3000) {
      return this.show(message, 'success', duration);
    }
  
    error(message, duration = 3000) {
      return this.show(message, 'error', duration);
    }
  
    warning(message, duration = 3000) {
      return this.show(message, 'warning', duration);
    }
  
    info(message, duration = 3000) {
      return this.show(message, 'info', duration);
    }
  }
  
  // Initialize toast manager when DOM is loaded
  document.addEventListener('DOMContentLoaded', () => {
    window.toastManager = new ToastManager();
  });
  
  // Export for manual use
  window.showToast = (message, category = 'info', duration = 3000) => {
    if (window.toastManager) {
      return window.toastManager.show(message, category, duration);
    }
  };
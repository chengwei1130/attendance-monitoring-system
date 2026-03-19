// Auto-hide flash messages
setTimeout(() => {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(flash => {
        flash.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => flash.remove(), 300);
    });
}, 5000);

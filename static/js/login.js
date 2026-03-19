// Auto-hide flash messages after 5 seconds
setTimeout(() => {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(flash => {
        flash.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => flash.remove(), 300);
    });
}, 5000);

// Auto-hide flash messages
setTimeout(() => {
const flashes = document.querySelectorAll('.flash');
flashes.forEach(flash => {
    flash.style.animation = 'slideOut 0.3s ease-out';
    setTimeout(() => flash.remove(), 300);
});
}, 5000);

// Add animation for slideOut
const style = document.createElement('style');
style.textContent = `
@keyframes slideOut {
    to {
        transform: translateX(400px);
        opacity: 0;
    }
}
`;
document.head.appendChild(style);

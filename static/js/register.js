// Preview uploaded image
document.getElementById('photo').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(event) {
            console.log('Image selected:', file.name);
        };
        reader.readAsDataURL(file);
    }
});

// Auto-hide flash messages
setTimeout(() => {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(flash => {
        flash.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => flash.remove(), 300);
    });
}, 5000);

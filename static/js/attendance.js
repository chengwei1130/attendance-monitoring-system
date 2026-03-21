const img = document.getElementById('camera-feeds');

img.addEventListener('load', function() {
    console.log('Camera feed loaded successfully');
});

img.addEventListener('error', function() {
    img.style.border = '3px solid #ef4444';
    img.alt = 'Camera feed unavailable';
});

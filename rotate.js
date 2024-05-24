let vinyl = document.querySelector('.vinyl');
let rotation = 0;

window.addEventListener('wheel', function(event) {
    // Determine the scroll direction
    if (event.deltaY > 0) {
        // Scroll down
        rotation += 10;
    } else {
        // Scroll up
        rotation -= 10;
    }

    vinyl.style.transform = `rotate(${rotation}deg)`;

    // Prevent scrolling the page
    event.preventDefault();
    window.scrollTo(0, 0);
}, { passive: false });

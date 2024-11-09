const slider = document.querySelector('.slider');
let scrollAmount = 0;
const cardWidth = document.querySelector('.card').offsetWidth + 15; // Get width of a single card

function slideRight() {
    scrollAmount += cardWidth; // Move by one card's width
    slider.style.transform = `translateX(-${scrollAmount}px)`;
    checkLimits();
}

function slideLeft() {
    scrollAmount -= cardWidth; // Move by one card's width
    if (scrollAmount < 0) scrollAmount = 0;
    slider.style.transform = `translateX(-${scrollAmount}px)`;
    checkLimits();
}

function checkLimits() {
    const maxScroll = slider.scrollWidth - slider.clientWidth + cardWidth;
    if (scrollAmount >= maxScroll) {
        scrollAmount = maxScroll;
    } else if (scrollAmount <= 0) {
        scrollAmount = 0;
    }
}

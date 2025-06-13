document.addEventListener('DOMContentLoaded', () => {
    // This modern API is great for performance. It only runs when an element enters the screen.
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Add a delay based on a CSS variable for staggering effects
                const delay = getComputedStyle(entry.target).getPropertyValue('--delay') || '0s';
                entry.target.style.transitionDelay = delay;
                entry.target.classList.add('is-visible');
                // We only want the animation to run once, so we can unobserve it.
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1 // Trigger when 10% of the element is visible
    });

    const elementsToAnimate = document.querySelectorAll('.animate-on-scroll');
    elementsToAnimate.forEach(el => observer.observe(el));
});
// ==========================================================================
// Date calculations
// ==========================================================================

function calculateAge(birthDate) {
    const birth = new Date(birthDate);
    const today = new Date();
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
        age--;
    }
    return age;
}

function calculateYearsOfExperience(startDate) {
    const start = new Date(startDate);
    const today = new Date();
    const years = (today - start) / (1000 * 60 * 60 * 24 * 365.25);
    return Math.round(years);
}

// Update dynamic values
document.addEventListener('DOMContentLoaded', () => {
    const ageEl = document.getElementById('age');
    const expEl = document.getElementById('experience');
    const yearEl = document.getElementById('year');

    if (ageEl && ageEl.dataset.birth) {
        ageEl.textContent = calculateAge(ageEl.dataset.birth);
    }

    if (expEl && expEl.dataset.start) {
        expEl.textContent = calculateYearsOfExperience(expEl.dataset.start);
    }

    if (yearEl) {
        yearEl.textContent = new Date().getFullYear();
    }
});

// ==========================================================================
// Mobile menu
// ==========================================================================

const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const mobileMenu = document.getElementById('mobile-menu');

if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener('click', () => {
        mobileMenu.classList.toggle('hidden');
    });

    // Close menu on link click
    mobileMenu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            mobileMenu.classList.add('hidden');
        });
    });
}

// ==========================================================================
// Scroll animations (simple AOS replacement)
// ==========================================================================

function initScrollAnimations() {
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const delay = entry.target.dataset.aosDelay || 0;
                setTimeout(() => {
                    entry.target.classList.add('aos-animate');
                }, delay);
            }
        });
    }, observerOptions);

    document.querySelectorAll('[data-aos]').forEach(el => {
        observer.observe(el);
    });
}

document.addEventListener('DOMContentLoaded', initScrollAnimations);

// ==========================================================================
// Language bars animation
// ==========================================================================

function animateLanguageBars() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('.language-bar').forEach(bar => {
        observer.observe(bar);
    });
}

document.addEventListener('DOMContentLoaded', animateLanguageBars);

// ==========================================================================
// Card hover light effect
// ==========================================================================

function initCardHoverEffect() {
    document.querySelectorAll('.project-card, .liquid-button-primary').forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            card.style.setProperty('--mouse-x', `${x}px`);
            card.style.setProperty('--mouse-y', `${y}px`);
        });
    });
}

document.addEventListener('DOMContentLoaded', initCardHoverEffect);

// ==========================================================================
// Smooth scroll for anchor links
// ==========================================================================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ==========================================================================
// Navbar background on scroll
// ==========================================================================

let lastScroll = 0;
const nav = document.querySelector('nav');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;

    if (currentScroll > 100) {
        nav.style.opacity = '0.98';
    } else {
        nav.style.opacity = '1';
    }

    lastScroll = currentScroll;
});

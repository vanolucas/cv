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
    const expEl = document.getElementById('years-experience');
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
        const isHidden = mobileMenu.classList.toggle('hidden');
        // Add enhanced blur class to nav when menu is open
        const nav = document.querySelector('nav');
        if (nav) {
            nav.classList.toggle('menu-open', !isHidden);
        }
    });

    // Close menu on link click
    mobileMenu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            mobileMenu.classList.add('hidden');
            const nav = document.querySelector('nav');
            if (nav) {
                nav.classList.remove('menu-open');
            }
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
        nav.classList.add('scrolled');
    } else {
        nav.classList.remove('scrolled');
    }

    lastScroll = currentScroll;
});

// ==========================================================================
// Active section highlighting in navigation
// ==========================================================================

function updateActiveNavLink() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link, .nav-link-mobile');

    const scrollPosition = window.scrollY + window.innerHeight / 3;

    let activeSection = null;

    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;
        const sectionId = section.getAttribute('id');

        if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
            activeSection = sectionId;
        }
    });

    // Special case: if at the very top, activate profile
    if (window.scrollY < 100) {
        activeSection = 'profile';
    }

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && href.startsWith('#')) {
            const targetId = href.substring(1);

            if (targetId === activeSection) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        }
    });
}

// Throttle scroll event for better performance
let scrollTimeout;
window.addEventListener('scroll', () => {
    if (scrollTimeout) {
        window.cancelAnimationFrame(scrollTimeout);
    }

    scrollTimeout = window.requestAnimationFrame(() => {
        updateActiveNavLink();
    });
});

// Initial check on page load
document.addEventListener('DOMContentLoaded', updateActiveNavLink);

// ==========================================================================
// Theme toggle (light/dark mode)
// ==========================================================================

function getPreferredTheme() {
    const stored = localStorage.getItem('theme');
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    setTheme(current === 'dark' ? 'light' : 'dark');
}

// Bind toggle buttons
document.getElementById('theme-toggle')?.addEventListener('click', toggleTheme);
document.getElementById('theme-toggle-mobile')?.addEventListener('click', toggleTheme);

// Listen for system preference changes
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) {
        setTheme(e.matches ? 'dark' : 'light');
    }
});

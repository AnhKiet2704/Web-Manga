// Main JavaScript Functions

// Auto-hide messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.message');
    messages.forEach(msg => {
        setTimeout(() => {
            msg.style.transition = 'opacity 0.5s';
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 500);
        }, 5000);
    });
});

// Lazy Loading Images
function initLazyLoad() {
    const images = document.querySelectorAll('img[loading="lazy"]');

    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    img.classList.add('loaded');
                    observer.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px 0px',
            threshold: 0.01
        });

        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for browsers that don't support IntersectionObserver
        images.forEach(img => {
            if (img.dataset.src) {
                img.src = img.dataset.src;
            }
        });
    }
}

// Search with Enter key
const searchInput = document.querySelector('.search-box input');
if (searchInput) {
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            this.closest('form').submit();
        }
    });
}

// Confirm before logout
const logoutLinks = document.querySelectorAll('a[href*="/auth/logout/"]');
logoutLinks.forEach(link => {
    link.addEventListener('click', function(e) {
        if (!confirm('Bạn có chắc muốn đăng xuất?')) {
            e.preventDefault();
        }
    });
});

// Star Rating System
function initStarRating() {
    const starInputs = document.querySelectorAll('.star-rating input');
    const starLabels = document.querySelectorAll('.star-rating label');

    starLabels.forEach((label, index) => {
        label.addEventListener('mouseenter', function() {
            highlightStars(index);
        });

        label.addEventListener('click', function() {
            starInputs[index].checked = true;
        });
    });

    const ratingContainer = document.querySelector('.star-rating');
    if (ratingContainer) {
        ratingContainer.addEventListener('mouseleave', function() {
            const checked = document.querySelector('.star-rating input:checked');
            if (checked) {
                const checkedIndex = Array.from(starInputs).indexOf(checked);
                highlightStars(checkedIndex);
            } else {
                clearStars();
            }
        });
    }

    function highlightStars(index) {
        starLabels.forEach((label, i) => {
            if (i <= index) {
                label.style.color = '#ffc107';
            } else {
                label.style.color = '#ddd';
            }
        });
    }

    function clearStars() {
        starLabels.forEach(label => {
            label.style.color = '#ddd';
        });
    }
}

// Smooth Scroll to Top
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Add scroll to top button
function addScrollTopButton() {
    const scrollBtn = document.createElement('button');
    scrollBtn.innerHTML = '↑';
    scrollBtn.className = 'scroll-top-btn';
    scrollBtn.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: #007bff;
        color: white;
        border: none;
        font-size: 24px;
        cursor: pointer;
        display: none;
        z-index: 1000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        transition: all 0.3s;
    `;

    scrollBtn.addEventListener('click', scrollToTop);
    document.body.appendChild(scrollBtn);

    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollBtn.style.display = 'block';
        } else {
            scrollBtn.style.display = 'none';
        }
    });
}

// Image Error Handling
function handleImageError() {
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.addEventListener('error', function() {
            this.src = '/static/images/placeholder.png';
            this.alt = 'Image not found';
        });
    });
}

// Local Storage for Reading Preferences
function saveReadingPosition(mangaId, chapterId, scrollPosition) {
    const key = `reading_${mangaId}_${chapterId}`;
    localStorage.setItem(key, scrollPosition);
}

function getReadingPosition(mangaId, chapterId) {
    const key = `reading_${mangaId}_${chapterId}`;
    return localStorage.getItem(key);
}

// Auto-save reading position
if (window.location.pathname.includes('/manga/')) {
    window.addEventListener('scroll', function() {
        const path = window.location.pathname.split('/');
        if (path.length >= 4) {
            const mangaSlug = path[2];
            const chapterSlug = path[3];
            saveReadingPosition(mangaSlug, chapterSlug, window.pageYOffset);
        }
    });
}

// Comment Form Enhancement
function initCommentForm() {
    const commentForms = document.querySelectorAll('.comment-form');
    commentForms.forEach(form => {
        const textarea = form.querySelector('textarea');
        if (textarea) {
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = this.scrollHeight + 'px';
            });
        }
    });
}

// Mobile Menu Toggle
function initMobileMenu() {
    const header = document.querySelector('.header');
    const nav = document.querySelector('.main-nav');

    if (window.innerWidth < 768) {
        const menuBtn = document.createElement('button');
        menuBtn.innerHTML = '☰';
        menuBtn.className = 'mobile-menu-btn';
        menuBtn.style.cssText = `
            display: block;
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
        `;

        menuBtn.addEventListener('click', function() {
            nav.classList.toggle('active');
        });

        header.insertBefore(menuBtn, nav);
    }
}

// Initialize all functions
document.addEventListener('DOMContentLoaded', function() {
    initLazyLoad();
    initStarRating();
    addScrollTopButton();
    handleImageError();
    initCommentForm();
    initMobileMenu();
});

// AJAX for Follow/Unfollow (optional enhancement)
function handleFollowAction(mangaId, isFollowing) {
    fetch(`/follow/${mangaId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    })
    .catch(error => console.error('Error:', error));
}

// Get CSRF Token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Reading Progress Bar
function initReadingProgress() {
    const progressBar = document.createElement('div');
    progressBar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        height: 3px;
        background: #007bff;
        width: 0%;
        z-index: 9999;
        transition: width 0.2s;
    `;
    document.body.appendChild(progressBar);

    window.addEventListener('scroll', function() {
        const windowHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrolled = (window.pageYOffset / windowHeight) * 100;
        progressBar.style.width = scrolled + '%';
    });
}

// Initialize reading progress on reader pages
if (window.location.pathname.includes('/manga/') &&
    window.location.pathname.split('/').length > 3) {
    initReadingProgress();
}
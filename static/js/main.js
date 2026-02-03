/**
 * FLEXS - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {
    // Mobile menu toggle
    initMobileMenu();

    // Messages auto-close
    initMessages();

    // Smooth scroll
    initSmoothScroll();

    // AJAX cart
    initAjaxCart();
});

/**
 * Mobile Menu Toggle
 */
function initMobileMenu() {
    const menuBtn = document.querySelector('.mobile-menu-btn');
    const navMain = document.querySelector('.nav-main');

    if (menuBtn && navMain) {
        menuBtn.addEventListener('click', function () {
            navMain.classList.toggle('open');
            menuBtn.classList.toggle('active');
        });
    }

    // Panel sidebar toggle
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const panelSidebar = document.querySelector('.panel-sidebar');

    if (sidebarToggle && panelSidebar) {
        sidebarToggle.addEventListener('click', function () {
            panelSidebar.classList.toggle('open');
        });
    }
}

/**
 * Auto-close Messages
 */
function initMessages() {
    const messages = document.querySelectorAll('.message');

    messages.forEach(function (message) {
        // Auto close after 5 seconds
        setTimeout(function () {
            message.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(function () {
                message.remove();
            }, 300);
        }, 5000);

        // Close button
        const closeBtn = message.querySelector('.message-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function () {
                message.style.animation = 'slideOut 0.3s ease forwards';
                setTimeout(function () {
                    message.remove();
                }, 300);
            });
        }
    });
}

/**
 * Smooth Scroll for anchor links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                const headerHeight = 70;
                const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight;

                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * AJAX Add to Cart
 */
function initAjaxCart() {
    document.querySelectorAll('.ajax-add-cart').forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            const formData = new FormData(this);
            const url = this.action;
            const button = this.querySelector('button[type="submit"]');
            const originalText = button.innerHTML;

            button.innerHTML = '⏳';
            button.disabled = true;

            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update cart count
                        const cartCount = document.querySelector('.cart-count');
                        if (cartCount) {
                            cartCount.textContent = data.total_items;
                        }

                        // Show success message
                        showNotification(data.message, 'success');

                        button.innerHTML = '✓';
                        setTimeout(() => {
                            button.innerHTML = originalText;
                            button.disabled = false;
                        }, 1500);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    button.innerHTML = originalText;
                    button.disabled = false;
                });
        });
    });
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    const container = document.querySelector('.messages-container') || createMessagesContainer();

    const notification = document.createElement('div');
    notification.className = `message message-${type}`;
    notification.innerHTML = `
        ${message}
        <button class="message-close">&times;</button>
    `;

    container.appendChild(notification);

    // Auto close
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => notification.remove(), 300);
    }, 3000);

    // Close button
    notification.querySelector('.message-close').addEventListener('click', () => {
        notification.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => notification.remove(), 300);
    });
}

function createMessagesContainer() {
    const container = document.createElement('div');
    container.className = 'messages-container';
    document.body.appendChild(container);
    return container;
}

// Add slideOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

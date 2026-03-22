// static/admin/js/custom_admin.js

document.addEventListener('DOMContentLoaded', function() {
    // Добавляем аватар пользователя в навигационную панель
    const userMenu = document.querySelector('.user-menu');
    if (userMenu) {
        const userAvatar = document.createElement('div');
        userAvatar.className = 'user-avatar';

        // Получаем имя пользователя из элемента
        const userNameElement = document.querySelector('.user-name');
        if (userNameElement) {
            const userName = userNameElement.textContent;
            userAvatar.textContent = userName.charAt(0).toUpperCase();
        }

        const userInfo = document.querySelector('.user-info');
        if (userInfo && !userInfo.querySelector('.user-avatar')) {
            userInfo.insertBefore(userAvatar, userInfo.firstChild);
        }
    }

    // Добавляем анимацию для карточек
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.05}s`;
        card.style.animation = 'fadeIn 0.5s ease forwards';
        card.style.opacity = '0';
        setTimeout(() => {
            card.style.opacity = '1';
        }, index * 50);
    });

    // Кастомизация модальных окон
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
            document.body.style.overflow = 'hidden';
        });

        modal.addEventListener('hidden.bs.modal', function() {
            document.body.style.overflow = 'auto';
        });
    });

    // Улучшаем обработку форм
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Сохранение...';

                // Восстанавливаем кнопку через 30 секунд (на случай ошибки)
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = submitBtn.getAttribute('data-original-text') || 'Сохранить';
                }, 30000);
            }
        });
    });

    // Добавляем плавную прокрутку для якорей
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Подсветка активного пункта меню
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && href !== '#' && currentPath.includes(href)) {
            link.classList.add('active');
            // Раскрываем родительское меню
            const parentNav = link.closest('.nav-treeview');
            if (parentNav) {
                const parentItem = parentNav.closest('.nav-item');
                if (parentItem) {
                    parentItem.classList.add('menu-open');
                    const parentLink = parentItem.querySelector('.nav-link');
                    if (parentLink) {
                        parentLink.classList.add('active');
                    }
                }
            }
        }
    });

    // Улучшаем поиск
    const searchInput = document.querySelector('.form-control[type="search"]');
    if (searchInput) {
        searchInput.placeholder = 'Поиск...';
        searchInput.addEventListener('focus', function() {
            this.style.borderColor = '#df3b3b';
            this.style.boxShadow = '0 0 0 3px rgba(223, 59, 59, 0.1)';
        });

        searchInput.addEventListener('blur', function() {
            this.style.borderColor = '#ced4da';
            this.style.boxShadow = 'none';
        });
    }

    // Уведомления
    const messages = document.querySelectorAll('.alert');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.transition = 'opacity 0.5s ease';
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 500);
        }, 5000);
    });
});

// Функция для подтверждения опасных действий
function confirmDangerousAction(message, callback) {
    if (confirm(message || 'Вы уверены, что хотите выполнить это действие?')) {
        callback();
    }
}

// Экспортируем функцию для глобального использования
window.confirmDangerousAction = confirmDangerousAction;

// Добавляем кастомные уведомления
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.style.borderRadius = '12px';
    notification.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
    notification.innerHTML = `
        ${message}
        <button type="button" class="close" data-dismiss="alert">&times;</button>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

window.showNotification = showNotification;
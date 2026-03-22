// static/admin/js/custom_admin.js

document.addEventListener('DOMContentLoaded', function() {
    // Плавное появление карточек
    const cards = document.querySelectorAll('.card, .small-box');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.animation = `fadeIn 0.3s ease forwards`;
        card.style.animationDelay = `${index * 0.03}s`;
    });

    // Эффект для кнопок
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            if (!this.classList.contains('btn-secondary')) {
                this.style.transform = 'translateY(-1px)';
            }
        });
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Авто-скрытие сообщений через 5 секунд
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.3s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // Подсветка строк таблицы при клике
    const tableRows = document.querySelectorAll('.table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('click', function(e) {
            if (e.target.tagName !== 'A' && e.target.tagName !== 'BUTTON') {
                tableRows.forEach(r => r.classList.remove('table-active'));
                this.classList.add('table-active');
            }
        });
    });

    // Улучшение полей ввода
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement?.querySelector('.form-label')?.classList.add('text-primary');
        });
        input.addEventListener('blur', function() {
            this.parentElement?.querySelector('.form-label')?.classList.remove('text-primary');
        });
    });

    // Подтверждение удаления
    const deleteButtons = document.querySelectorAll('.deletelink, .btn-danger');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите удалить этот элемент? Это действие нельзя отменить.')) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        });
    });

    // Добавление классов для лучшего вида
    const filterSidebar = document.querySelector('#changelist-filter');
    if (filterSidebar) {
        filterSidebar.classList.add('mb-4');
    }

    // Анимация для боковой панели на мобильных
    const sidebarToggle = document.querySelector('[data-widget="pushmenu"]');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.querySelector('.sidebar')?.classList.toggle('show');
        });
    }

    // Фокус на поле поиска по нажатию /
    document.addEventListener('keydown', function(e) {
        if (e.key === '/' && document.activeElement.tagName !== 'INPUT') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"]');
            if (searchInput) searchInput.focus();
        }
    });

    // Подсказка для поиска
    const searchInput = document.querySelector('input[type="search"]');
    if (searchInput && !searchInput.placeholder) {
        searchInput.placeholder = 'Поиск... (нажмите /)';
    }
});

// Функция для уведомлений
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed`;
    toast.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        max-width: 400px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: fadeIn 0.3s ease;
    `;
    toast.innerHTML = `
        <div class="d-flex align-items-center gap-2">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

window.showToast = showToast;
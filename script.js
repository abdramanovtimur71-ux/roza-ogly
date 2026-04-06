/* ============================================
   JAVASCRIPT - Интерактивность и Анимации
   ============================================ */

// Плавная прокрутка
function scrollToSection(selector) {
    const element = document.querySelector(selector);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

// Счетчик статистики
const animateCountUp = () => {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.animated) {
                const target = parseInt(entry.target.dataset.target);
                const increment = target / 100;
                let current = 0;
                
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        entry.target.textContent = target;
                        clearInterval(timer);
                    } else {
                        entry.target.textContent = Math.floor(current);
                    }
                }, 10);
                
                entry.target.animated = true;
            }
        });
    });
    
    statNumbers.forEach(number => observer.observe(number));
};

// Появление элементов при прокрутке
const observeElements = () => {
    const elements = document.querySelectorAll('.fade-in, .slide-in, .about-card, .service-item');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.animation = entry.target.classList.contains('fade-in') 
                    ? 'fadeIn 0.8s ease-out forwards' 
                    : 'slideUp 0.8s ease-out forwards';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    elements.forEach(el => observer.observe(el));
};

// Активная навигация при прокрутке
const updateActiveNav = () => {
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('.nav-link');
    
    window.addEventListener('scroll', () => {
        let current = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (pageYOffset >= sectionTop - 100) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    });
};

// Обработка отправки формы
const handleFormSubmit = () => {
    const form = document.querySelector('.contact-form');
    if (!form) return;
    
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Имитация отправки
        const submitBtn = form.querySelector('.submit-btn');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = '✓ Сообщение отправлено!';
        submitBtn.style.background = 'linear-gradient(135deg, #4CAF50, #45a049)';
        
        // Очистка формы
        form.reset();
        
        // Восстановление кнопки
        setTimeout(() => {
            submitBtn.textContent = originalText;
            submitBtn.style.background = 'linear-gradient(135deg, var(--primary), var(--secondary))';
        }, 3000);
    });
};

// Параллакс эффект при движении мыши
const mouseParallax = () => {
    const shapes = document.querySelectorAll('.floating-shape');
    
    document.addEventListener('mousemove', (e) => {
        const mouseX = e.clientX / window.innerWidth;
        const mouseY = e.clientY / window.innerHeight;
        
        shapes.forEach((shape, index) => {
            const speed = (index + 1) * 10;
            shape.style.transform = `translate(${mouseX * speed}px, ${mouseY * speed}px)`;
        });
    });
};

// Эффект появления навигации при прокрутке
const navbarScroll = () => {
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.boxShadow = '0 5px 20px rgba(0, 0, 0, 0.15)';
        } else {
            navbar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
        }
    });
};

// Анимация при наведении на карточки услуг
const serviceCardHover = () => {
    const serviceItems = document.querySelectorAll('.service-item');
    
    serviceItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05) rotateY(5deg)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1) rotateY(0deg)';
        });
    });
};

// Волновая анимация текста в заголовке
const waveAnimation = () => {
    const words = document.querySelectorAll('.hero-title .word');
    
    words.forEach((word, index) => {
        const letters = word.textContent.split('');
        word.textContent = '';
        
        letters.forEach((letter, letterIndex) => {
            const span = document.createElement('span');
            span.textContent = letter;
            span.style.display = 'inline-block';
            span.style.animation = `wave 0.5s ease-in-out ${letterIndex * 0.05}s`;
            word.appendChild(span);
        });
    });
};

// Добавления стиля для волны
const addWaveStyle = () => {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes wave {
            0%, 100% {
                transform: translateY(0);
            }
            50% {
                transform: translateY(-10px);
            }
        }
    `;
    document.head.appendChild(style);
};

// Прогрессивная загрузка изображений
const lazyLoad = () => {
    const images = document.querySelectorAll('img');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.style.opacity = '0';
                img.onload = () => {
                    img.style.transition = 'opacity 0.5s ease-out';
                    img.style.opacity = '1';
                };
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
};

// Инициализация всех функций при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    // Небольшая задержка для плавной инициализации
    requestAnimationFrame(() => {
        waveAnimation();
        addWaveStyle();
        observeElements();
        animateCountUp();
        updateActiveNav();
        handleFormSubmit();
        mouseParallax();
        navbarScroll();
        serviceCardHover();
        lazyLoad();
        
        // Добавляем активный класс к первой ссылке навигации
        const firstNavLink = document.querySelector('.nav-link');
        if (firstNavLink) {
            firstNavLink.classList.add('active');
        }
    });
});

// Обработка клавиатуры для навигации
document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowDown') {
        window.scrollBy({ top: 100, behavior: 'smooth' });
    } else if (e.key === 'ArrowUp') {
        window.scrollBy({ top: -100, behavior: 'smooth' });
    }
});

// Случайная позиция фигур при загрузке
window.addEventListener('load', () => {
    const shapes = document.querySelectorAll('.floating-shape');
    shapes.forEach(shape => {
        const randomX = Math.random() * 200 - 100;
        const randomY = Math.random() * 200 - 100;
        shape.style.left = randomX + 'px';
        shape.style.top = randomY + 'px';
    });
});

// Защита от потери данных в форме
const formProtection = () => {
    const formInputs = document.querySelectorAll('.contact-form input, .contact-form textarea');
    let hasChanges = false;
    
    formInputs.forEach(input => {
        input.addEventListener('change', () => {
            hasChanges = true;
        });
    });
    
    window.addEventListener('beforeunload', (e) => {
        if (hasChanges) {
            e.preventDefault();
            e.returnValue = '';
        }
    });
};

// Инициализация защиты формы
document.addEventListener('DOMContentLoaded', formProtection);

// Эффект свечения при фокусе на форме
const formGlowEffect = () => {
    const formInputs = document.querySelectorAll('.contact-form input, .contact-form textarea');
    
    formInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.1), 0 0 15px rgba(102, 126, 234, 0.3)';
        });
        
        input.addEventListener('blur', function() {
            this.style.boxShadow = 'none';
        });
    });
};

document.addEventListener('DOMContentLoaded', formGlowEffect);

/* ============================================
   ОПТИМИЗАЦИЯ И ПРОИЗВОДИТЕЛЬНОСТЬ
   ============================================ */

// Дебаунс функция для управления событиями
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Оптимизированная обработка скролла
window.addEventListener('scroll', debounce(() => {
    updateActiveNav();
    navbarScroll();
}, 100));

// Указание браузеру на предварительную загрузку ресурсов
if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
        // Предзагрузка изображений и других ресурсов
        const preloadLinks = document.querySelectorAll('link[rel="preload"]');
        preloadLinks.forEach(link => {
            link.rel = 'prefetch';
        });
    });
}

/* ============================================
   АУТЕНТИФИКАЦИЯ И МОДАЛЬНЫЕ ОКНА
   ============================================ */

const ADMIN_ACCESS_CODE = '0000';
const API_BASE = localStorage.getItem('apiBaseUrl') || 'http://127.0.0.1:5000';

function getStorageArray(key) {
    try {
        return JSON.parse(localStorage.getItem(key) || '[]');
    } catch {
        return [];
    }
}

function setStorageArray(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
}

function addAdminRecord(key, payload) {
    const items = getStorageArray(key);
    items.unshift({ id: Date.now(), createdAt: new Date().toISOString(), ...payload });
    setStorageArray(key, items.slice(0, 200));
}

async function openAdminAccess() {
    const code = window.prompt('Введите пароль спецвхода');
    if (!code) {
        return;
    }
    if (code.trim() !== ADMIN_ACCESS_CODE) {
        showError('Неверный код администратора');
        return;
    }
    try {
        const response = await fetch(API_BASE + '/api/admin/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: code.trim() })
        });
        const data = await response.json();
        if (!response.ok || !data.ok) {
            showError(data.message || 'Ошибка спецвхода');
            return;
        }
        localStorage.setItem('isAdminLoggedIn', 'true');
        localStorage.setItem('adminToken', data.token);
        window.location.href = 'admin.html';
    } catch (error) {
        showError('Сервер спецвхода недоступен');
    }
}

// Функции для работы с модальными окнами входа

function openLoginModal() {
    const modal = document.getElementById('loginModal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeLoginModal() {
    const modal = document.getElementById('loginModal');
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
}

function openRegistrationModal() {
    closeLoginModal();
    const modal = document.getElementById('registrationModal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeRegistrationModal() {
    const modal = document.getElementById('registrationModal');
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
}

// Закрытие модального окна при клике на фон
document.addEventListener('DOMContentLoaded', () => {
    const loginModal = document.getElementById('loginModal');
    const registrationModal = document.getElementById('registrationModal');
    
    window.addEventListener('click', (event) => {
        if (event.target === loginModal) {
            closeLoginModal();
        }
        if (event.target === registrationModal) {
            closeRegistrationModal();
        }
    });
    
    // Закрытие при нажатии Escape
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeLoginModal();
            closeRegistrationModal();
        }
    });
});

// Переключение видимости пароля
function togglePassword() {
    const passwordInput = document.getElementById('password');
    const button = event.target;
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        button.textContent = '🙈';
    } else {
        passwordInput.type = 'password';
        button.textContent = '👁️';
    }
}

function toggleRegistrationPassword() {
    const passwordInput = document.getElementById('reg-password');
    const button = event.target;
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        button.textContent = '🙈';
    } else {
        passwordInput.type = 'password';
        button.textContent = '👁️';
    }
}

// Обработка формы входа
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginFormElement');
    
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const rememberMe = document.getElementById('rememberMe').checked;
            
            // Валидация
            if (!email || !password) {
                showError('Пожалуйста, заполните все поля');
                return;
            }
            
            if (password.length < 6) {
                showError('Пароль должен содержать не менее 6 символов');
                return;
            }
            
            // Сохранение в localStorage (демонстрация)
            localStorage.setItem('userEmail', email);
            localStorage.setItem('isLoggedIn', 'true');
            if (!localStorage.getItem('userName')) {
                localStorage.setItem('userName', email.split('@')[0]);
            }
            
            if (rememberMe) {
                localStorage.setItem('rememberMe', 'true');
            }
            
            // Имитация входа
            simulateLogin(email);
        });
    }
});

// Обработка формы регистрации
document.addEventListener('DOMContentLoaded', () => {
    const registrationForm = document.getElementById('registrationFormElement');
    
    if (registrationForm) {
        registrationForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const name = document.getElementById('name').value;
            const email = document.getElementById('reg-email').value;
            const password = document.getElementById('reg-password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            const agree = document.getElementById('agree').checked;
            
            // Валидация
            if (!name || !email || !password || !confirmPassword) {
                showError('Пожалуйста, заполните все поля');
                return;
            }
            
            if (password.length < 8) {
                showError('Пароль должен содержать не менее 8 символов');
                return;
            }
            
            if (password !== confirmPassword) {
                showError('Пароли не совпадают');
                return;
            }
            
            if (!agree) {
                showError('Пожалуйста, согласитесь с условиями использования');
                return;
            }
            
            // Сохранение в localStorage (демонстрация)
            localStorage.setItem('userName', name);
            localStorage.setItem('userEmail', email);
            localStorage.setItem('isLoggedIn', 'true');

            addAdminRecord('registrations', {
                name,
                email,
                source: 'index-registration'
            });
            
            // Имитация регистрации
            simulateLogin(name);
        });
    }
});

// Функция для имитации входа
function simulateLogin(userName) {
    const loginBtn = document.querySelector('.login-btn');
    const userProfile = document.getElementById('userProfile');
    const profileAvatar = document.querySelector('.profile-avatar');
    
    if (loginBtn) loginBtn.style.display = 'none';
    
    userProfile.classList.remove('hidden');
    
    // Устанавливаем аватар с первой буквой имени
    if (profileAvatar) {
        profileAvatar.textContent = userName.charAt(0).toUpperCase();
    }
    
    closeRegistrationModal();
    closeLoginModal();
    
    // Показываем сообщение об успехе
    showSuccess(`Добро пожаловать, ${userName}!`);
    
    setTimeout(() => {
        window.location.href = 'dashboard.html';
    }, 800);
}

// Функция проверки статуса входа при загрузке страницы
function checkLoginStatus() {
    const userLogged = localStorage.getItem('isLoggedIn');
    const userName = localStorage.getItem('userName') || localStorage.getItem('userEmail');
    
    if (userLogged && userName) {
        const loginBtn = document.querySelector('.login-btn');
        const userProfile = document.getElementById('userProfile');
        const profileAvatar = document.querySelector('.profile-avatar');
        
        if (loginBtn) loginBtn.style.display = 'none';
        userProfile.classList.remove('hidden');
        userProfile.classList.remove('open');
        
        if (profileAvatar) {
            profileAvatar.textContent = userName.charAt(0).toUpperCase();
        }
    }
}

function toggleProfileMenu(event) {
    event.stopPropagation();
    const userProfile = document.getElementById('userProfile');
    if (!userProfile || userProfile.classList.contains('hidden')) {
        return;
    }
    userProfile.classList.toggle('open');
}

function setupProfileMenuInteractions() {
    const userProfile = document.getElementById('userProfile');
    if (!userProfile) {
        return;
    }

    document.addEventListener('click', (event) => {
        if (!userProfile.classList.contains('hidden') && !userProfile.contains(event.target)) {
            userProfile.classList.remove('open');
        }
    });

    userProfile.querySelectorAll('.profile-link').forEach((link) => {
        link.addEventListener('click', () => {
            userProfile.classList.remove('open');
        });
    });
}

// Функция выхода
function logout() {
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('userName');
    localStorage.removeItem('userEmail');
    localStorage.removeItem('rememberMe');
    
    const loginBtn = document.querySelector('.login-btn');
    const userProfile = document.getElementById('userProfile');
    
    if (loginBtn) loginBtn.style.display = 'block';
    userProfile.classList.add('hidden');
    
    showSuccess('Вы успешно вышли из сессии');
}

// Обработка формы записи на главной странице
document.addEventListener('DOMContentLoaded', () => {
    const bookingForm = document.getElementById('bookingFormElement');
    if (!bookingForm) {
        return;
    }

    bookingForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const nameField = bookingForm.querySelector('input[type="text"]');
        const phoneField = bookingForm.querySelector('input[type="tel"]');
        const emailField = bookingForm.querySelector('input[type="email"]');
        const serviceField = bookingForm.querySelector('select');
        const dateField = bookingForm.querySelector('input[type="date"]');
        const timeField = bookingForm.querySelector('input[type="time"]');
        const noteField = bookingForm.querySelector('textarea');

        const payload = {
            name: nameField ? nameField.value.trim() : '',
            phone: phoneField ? phoneField.value.trim() : '',
            email: emailField ? emailField.value.trim() : '',
            service: serviceField ? serviceField.options[serviceField.selectedIndex].text : '',
            date: dateField ? dateField.value : '',
            time: timeField ? timeField.value : '',
            format: 'Запись через сайт',
            note: noteField ? noteField.value.trim() : ''
        };

        try {
            const response = await fetch(API_BASE + '/api/bookings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            if (!response.ok) {
                if (data && data.conflict) {
                    showError((data.message || 'Это время занято') + (data.suggestedTime ? (' Рекомендуем: ' + data.suggestedTime) : ''));
                    return;
                }
                showError(data.message || 'Не удалось записаться');
                return;
            }

            addAdminRecord('bookings', {
                name: payload.name || 'Не указано',
                email: payload.email || 'Не указано',
                service: payload.service || 'Не указано',
                date: payload.date,
                time: payload.time,
                source: 'index-booking-api'
            });

            bookingForm.reset();
            showSuccess('Вы успешно записаны. Уведомления отправлены автоматически.');
        } catch (error) {
            showError('Сервер записи недоступен. Проверьте backend и повторите попытку.');
        }
    });
});

function renderGuestReviews() {
    const list = document.getElementById('guestReviewsList');
    if (!list) {
        return;
    }

    const defaults = [
        { name: 'Айгерим', rating: 5, text: 'Очень спокойная и профессиональная консультация. После сеанса стало легче принимать решения.' },
        { name: 'Нурлан', rating: 5, text: 'Понравилась точность расклада и поддержка после встречи. Рекомендую.' },
        { name: 'Жанна', rating: 4, text: 'Уютная атмосфера и сильная энергетика. Спасибо за внимание к деталям.' }
    ];

    const stored = getStorageArray('guestReviews');
    const reviews = stored.length ? stored : defaults;

    list.innerHTML = reviews
        .slice(0, 12)
        .map((item) => {
            const stars = '★★★★★'.slice(0, Number(item.rating || 5)) + '☆☆☆☆☆'.slice(0, 5 - Number(item.rating || 5));
            return `
                <article class="guest-item">
                    <div class="guest-item-head">
                        <span class="guest-item-name">${item.name}</span>
                        <span class="guest-item-stars">${stars}</span>
                    </div>
                    <p class="guest-item-text">${item.text}</p>
                </article>
            `;
        })
        .join('');
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('guestReviewForm');
    renderGuestReviews();

    if (!form) {
        return;
    }

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const name = document.getElementById('guestName').value.trim();
        const rating = Number(document.getElementById('guestRating').value || 5);
        const text = document.getElementById('guestText').value.trim();

        if (!name || !text) {
            showError('Заполните имя и текст отзыва');
            return;
        }

        const items = getStorageArray('guestReviews');
        items.unshift({ name, rating, text, createdAt: new Date().toISOString() });
        setStorageArray('guestReviews', items.slice(0, 40));
        addAdminRecord('guestReviews', { name, rating, text, source: 'site-guest-review' });

        form.reset();
        renderGuestReviews();
        showSuccess('Спасибо! Ваш отзыв опубликован.');
    });
});

async function renderPublicContent() {
    const root = document.getElementById('publicContentList');
    if (!root) {
        return;
    }

    try {
        const response = await fetch(API_BASE + '/api/content');
        const data = await response.json();
        if (!response.ok || !data.ok) {
            root.innerHTML = '<div class="public-item"><p>Материалы скоро появятся.</p></div>';
            return;
        }

        const names = {
            story: 'История',
            doc: 'Документ',
            photo: 'Фото',
            video: 'Видео'
        };

        const items = (data.items || []).slice(0, 20);
        if (!items.length) {
            root.innerHTML = '<div class="public-item"><p>Пока нет публикаций.</p></div>';
            return;
        }

        root.innerHTML = items.map((item) => {
            const kind = names[item.kind] || item.kind;
            const link = item.media_url ? '<a href="' + item.media_url + '" target="_blank" rel="noopener noreferrer">Открыть</a>' : '';
            const body = item.body ? item.body : 'Без описания';
            return '<article class="public-item">'
                + '<div class="kind">' + kind + '</div>'
                + '<h3>' + (item.title || 'Без названия') + '</h3>'
                + '<p>' + body + '</p>'
                + link
                + '</article>';
        }).join('');
    } catch (error) {
        root.innerHTML = '<div class="public-item"><p>Не удалось загрузить публикации.</p></div>';
    }
}

document.addEventListener('DOMContentLoaded', renderPublicContent);

// Показ сообщения об ошибке
function showError(message) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #E74C3C;
        color: white;
        padding: 16px 24px;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        z-index: 9999;
        animation: slideUp 0.3s ease;
        font-weight: 600;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'fadeIn 0.3s ease reverse';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// Показ сообщения об успехе
function showSuccess(message) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #27AE60;
        color: white;
        padding: 16px 24px;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        z-index: 9999;
        animation: slideUp 0.3s ease;
        font-weight: 600;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'fadeIn 0.3s ease reverse';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

/* ============================================
   ИНТЕРАКТИВНЫЕ ФУНКЦИИ
   ============================================ */

// Данные для гаданий
const tarotCards = [
    { name: "Маг", meaning: "Начало, инициатива, самоопределение" },
    { name: "Верховная Жрица", meaning: "Интуиция, миролюбивость, скрытые знания" },
    { name: "Императрица", meaning: "Плодородие, красота, природная власть" },
    { name: "Император", meaning: "Власть, лидерство, отцовство" },
    { name: "Иерофант", meaning: "Духовность, ритуал, традиция" },
    { name: "Влюбленные", meaning: "Любовь, гармония, ценности" },
    { name: "Колесница", meaning: "Контроль, воля, целеустремленность" },
    { name: "Отшельник", meaning: "Размышление, осторожность, поиск" },
    { name: "Колесо Судьбы", meaning: "Судьба, новые циклы, удача" },
    { name: "Справедливость", meaning: "Справедливость, равновесие, правда" }
];

const dailyAdvices = [
    "Сегодня - хороший день для новых начинаний. Не бойтесь делать первый шаг!",
    "Обратите внимание на свою интуицию. Она подскажет вам правильный путь.",
    "День благоприятен для медитации и размышлений. Найдите время для себя.",
    "Энергия сегодня поддерживает общение с любимыми людьми. Свяжитесь с ними!",
    "День требует действия. Не откладывайте важные дела на потом.",
    "Слушайте звёзды. Вселенная посылает вам положительные знак.",
    "Хороший день для творчества и самовыражения. Позвольте себе быть собой.",
    "День благоприятен для переговоров и компромиссов.",
    "Сегодня хороший день для исцеления и гармонии. Позаботьтесь о себе.",
    "Энергия дня поддерживает финансовые начинания. Рассмотрите возможности."
];

// Тест совместимости
function runCompatibilityTest() {
    const q1 = document.querySelector('input[name="q1"]:checked');
    const q2 = document.querySelector('input[name="q2"]:checked');
    const q3 = document.querySelector('input[name="q3"]:checked');
    
    if (!q1 || !q2 || !q3) {
        showError('Пожалуйста, ответьте на все вопросы!');
        return;
    }
    
    const recommendations = {
        'decisions-believe-once': {
            service: '🎴 Таро Чтение',
            description: 'Вам подойдет классическое таро чтение для получения ясности в принятии решений.'
        },
        'loved-believe-once': {
            service: '👻 Контакт с Духами',
            description: 'Вам рекомендуется сеанс контакта с духами для общения с близкими.'
        },
        'health-believe-once': {
            service: '💎 Рейки Исцеление',
            description: 'Энергетическое исцеление Рейки поможет вам восстановить здоровье.'
        },
        'future-believe-constant': {
            service: '🌙 Астрологическая Консультация',
            description: 'Анализ вашей натальной карты раскроет планы судьбы на долгие годы.'
        },
        'decisions-experience-regular': {
            service: '🎯 Духовное Наставничество',
            description: 'Регулярное наставничество поможет вам развить свои способности.'
        },
        'default': {
            service: '🔮 Комплексное Исцеление',
            description: 'Рекомендуется комбинированный подход с несколькими услугами для максимального эффекта.'
        }
    };
    
    const key = q1.value + '-' + q2.value + '-' + q3.value;
    const recommendation = recommendations[key] || recommendations['default'];
    
    const resultDiv = document.getElementById('quizResult');
    const resultContent = document.getElementById('resultContent');
    
    resultContent.innerHTML = `
        <h4 style="color: var(--primary); margin-bottom: 10px; font-size: 20px;">
            ${recommendation.service}
        </h4>
        <p style="margin: 0; line-height: 1.6;">
            ${recommendation.description}
        </p>
    `;
    
    resultDiv.classList.remove('hidden');
    resultDiv.scrollIntoView({ behavior: 'smooth' });
}

// Гадание с картами таро
function drawTarotCard() {
    const cardResult = document.getElementById('cardResult');
    const randomIndex = Math.floor(Math.random() * tarotCards.length);
    const card = tarotCards[randomIndex];
    
    cardResult.innerHTML = `
        <h4 style="color: var(--primary); margin-bottom: 10px;">Ваша Карта: ${card.name}</h4>
        <p style="margin: 0; font-size: 14px; line-height: 1.6;">
            <strong>Значение:</strong> ${card.meaning}
        </p>
    `;
    cardResult.classList.remove('hidden');
}

// Число удачи
function getLuckyNumber() {
    const numberResult = document.getElementById('numberResult');
    const luckyNumber = Math.floor(Math.random() * 100) + 1;
    const significance = {
        lucky: luckyNumber % 2 === 0 ? 'четное (стабильность)' : 'нечетное (динамика)',
        meaning: luckyNumber < 33 ? 'энергия новых начинаний' : luckyNumber < 67 ? 'баланс и гармония' : 'высокая вибрация и успех'
    };
    
    numberResult.innerHTML = `
        <h4 style="color: var(--primary); margin-bottom: 10px; font-size: 32px; font-weight: 700;">
            ✨ ${luckyNumber}
        </h4>
        <p style="margin: 0; font-size: 14px;">
            <strong>Тип:</strong> ${significance.lucky}<br>
            <strong>Значение:</strong> ${significance.meaning}
        </p>
    `;
    numberResult.classList.remove('hidden');
}

// Совет дня
function getDailyAdvice() {
    const adviceResult = document.getElementById('adviceResult');
    const randomIndex = Math.floor(Math.random() * dailyAdvices.length);
    const advice = dailyAdvices[randomIndex];
    
    adviceResult.innerHTML = `
        <p style="margin: 0; font-size: 16px; line-height: 1.8; font-style: italic;">
            "💫 ${advice}"
        </p>
    `;
    adviceResult.classList.remove('hidden');
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', checkLoginStatus);
document.addEventListener('DOMContentLoaded', setupProfileMenuInteractions);

/* ============================================
   ПЕРЕКЛЮЧЕНИЕ ТЕМ
   ============================================ */

// Переключение между светлой и темной темой
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Обновляем иконку
    updateThemeIcon(newTheme);
}

// Обновление иконки переключателя
function updateThemeIcon(theme) {
    const toggle = document.getElementById('themeToggle');
    if (toggle) {
        toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
}

// Инициализация темы при загрузке
function initializeTheme() {
    const html = document.documentElement;
    const savedTheme = localStorage.getItem('theme');
    
    // Проверяем предпочтение в localStorage
    if (savedTheme) {
        html.setAttribute('data-theme', savedTheme);
        updateThemeIcon(savedTheme);
    } else {
        // Проверяем системные предпочтения
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
            html.setAttribute('data-theme', 'light');
            updateThemeIcon('light');
        } else {
            html.setAttribute('data-theme', 'dark');
            updateThemeIcon('dark');
        }
    }
}

// Инициализация темы при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    initializeTheme();
});

// Отслеживание изменений системной темы
if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            const newTheme = e.matches ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            updateThemeIcon(newTheme);
        }
    });
}

/* ============================================
   МОБИЛЬНОЕ МЕНЮ
   ============================================ */

function toggleMobileMenu() {
    const links = document.querySelector('.nav-links');
    const btn = document.getElementById('navHamburger');
    if (!links || !btn) return;
    const isOpen = links.classList.toggle('mobile-open');
    btn.classList.toggle('open', isOpen);
    document.body.style.overflow = isOpen ? 'hidden' : '';
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            const links = document.querySelector('.nav-links');
            const btn = document.getElementById('navHamburger');
            if (links) links.classList.remove('mobile-open');
            if (btn) btn.classList.remove('open');
            document.body.style.overflow = '';
        });
    });
});

/* ============================================
   КНОПКА "НАВЕРХ"
   ============================================ */

function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

window.addEventListener('scroll', () => {
    const btn = document.getElementById('scrollTopBtn');
    if (btn) btn.classList.toggle('visible', window.scrollY > 400);
});

/* ============================================
   FAQ АККОРДЕОН
   ============================================ */

function toggleFaq(questionEl) {
    const item = questionEl.closest('.faq-item');
    const isOpen = item.classList.contains('open');
    document.querySelectorAll('.faq-item.open').forEach(i => {
        i.classList.remove('open');
        i.querySelector('.faq-answer').style.maxHeight = null;
    });
    if (!isOpen) {
        item.classList.add('open');
        const inner = item.querySelector('.faq-answer-inner');
        item.querySelector('.faq-answer').style.maxHeight = inner.scrollHeight + 'px';
    }
}

/* ============================================
   ПРЕЛОАДЕР
   ============================================ */

window.addEventListener('load', () => {
    const preloader = document.getElementById('preloader');
    if (preloader) {
        setTimeout(() => preloader.classList.add('hidden'), 1400);
    }
});


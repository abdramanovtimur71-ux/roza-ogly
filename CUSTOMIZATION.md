# 🎨 Руководство по Кастомизации

## Быстрые Изменения

### 1. Измените Основной Текст
В `index.html` найдите и измените:

```html
<!-- Герой секция -->
<h1 class="hero-title">
    <span class="word">Добро</span>
    <span class="word">Пожаловать</span>
</h1>
<p class="hero-subtitle">Ваш путь к успеху начинается здесь</p>

<!-- О компании -->
<h2 class="section-title">Обо мне</h2>

<!-- Контактная информация -->
<p>info@roza-ogli.com</p>
<p>+7 (999) 123-45-67</p>
<p>Баку, Азербайджан</p>
```

### 2. Измените Цветовую Схему
В `styles.css` измените переменные:

```css
:root {
    /* Розовый/Красный градиент */
    --primary: #FF1493;           /* Основной цвет */
    --secondary: #FF69B4;         /* Вторичный цвет */
    --accent: #FFB6C1;            /* Акцентный цвет */
    --dark: #1A1A1A;              /* Темный текст */
    --light: #FFF0F5;             /* Светлый фон */
}
```

#### Рекомендуемые палитры:

**Профессиональная (Синяя)**
```css
--primary: #0066cc;
--secondary: #0099ff;
--accent: #FFD700;
```

**Творческая (Фиолетовая)**
```css
--primary: #9D4EDD;
--secondary: #C77DFF;
--accent: #E0AAFF;
```

**Энергичная (Оранжевая)**
```css
--primary: #FF6B35;
--secondary: #F7931E;
--accent: #FDB833;
```

**Мирная (Зеленая)**
```css
--primary: #06A77D;
--secondary: #22B8AA;
--accent: #91E5D9;
```

### 3. Добавьте Логотип

Замените текстовой логотип на изображение:

```html
<!-- Было -->
<div class="logo">
    <span class="logo-text">Роза Оглы</span>
</div>

<!-- Стало -->
<div class="logo">
    <img src="logo.png" alt="Роза Оглы" style="height: 40px;">
</div>
```

Обновите CSS:
```css
.logo {
    font-size: 24px;
    font-weight: 700;
    /* Удалите gradient */
}

.logo img {
    height: 40px;
    width: auto;
    transition: all 0.3s ease;
}

.logo img:hover {
    filter: brightness(1.2);
}
```

### 4. Добавьте Фоновое Изображение

```css
.hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%),
                url('your-image.jpg') center/cover;
    background-blend-mode: overlay;
}
```

### 5. Интегрируйте Социальные Сети

В `index.html` обновите футер:

```html
<div class="social-links">
    <a href="https://facebook.com/yourprofile" class="social-link">
        <i class="fab fa-facebook"></i>
    </a>
    <a href="https://instagram.com/yourprofile" class="social-link">
        <i class="fab fa-instagram"></i>
    </a>
    <a href="https://linkedin.com/in/yourprofile" class="social-link">
        <i class="fab fa-linkedin"></i>
    </a>
    <a href="https://twitter.com/yourprofile" class="social-link">
        <i class="fab fa-twitter"></i>
    </a>
</div>
```

Добавьте иконки Font Awesome в `<head>`:
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
```

### 6. Добавьте Видео на Герой

```html
<div class="hero-image">
    <video autoplay muted loop style="width: 100%; height: 100%; object-fit: cover; border-radius: 15px;">
        <source src="hero-video.mp4" type="video/mp4">
    </video>
</div>
```

### 7. Добавьте Галерею Портфолио

Создайте новую секцию в HTML:

```html
<section id="portfolio" class="portfolio">
    <div class="container">
        <h2 class="section-title">Portfolio</h2>
        <div class="portfolio-grid">
            <div class="portfolio-item">
                <img src="project1.jpg" alt="Project 1">
                <h3>Проект 1</h3>
                <p>Описание проекта</p>
            </div>
            <div class="portfolio-item">
                <img src="project2.jpg" alt="Project 2">
                <h3>Проект 2</h3>
                <p>Описание проекта</p>
            </div>
        </div>
    </div>
</section>
```

Добавьте CSS:
```css
.portfolio {
    padding: 100px 0;
    background: var(--white);
}

.portfolio-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 30px;
}

.portfolio-item {
    border-radius: 15px;
    overflow: hidden;
    background: var(--light);
    transition: all 0.3s ease;
}

.portfolio-item:hover {
    transform: translateY(-10px);
    box-shadow: var(--shadow-lg);
}

.portfolio-item img {
    width: 100%;
    height: 200px;
    object-fit: cover;
}

.portfolio-item h3 {
    padding: 20px;
    margin: 0;
}

.portfolio-item p {
    padding: 0 20px 20px 20px;
    color: #666;
}
```

## Продвинутые Настройки

### 1. Добавьте Dark Mode

Создайте переключатель в HTML:
```html
<button class="theme-toggle" id="themeToggle">🌙</button>
```

Добавьте в CSS:
```css
:root[data-theme="dark"] {
    --dark: #FFFFFF;
    --light: #1a1a1a;
    --white: #2d2d2d;
    --primary: #FF6B6B;
}

.theme-toggle {
    position: fixed;
    top: 20px;
    right: 20px;
    background: var(--primary);
    border: none;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    cursor: pointer;
    font-size: 24px;
    z-index: 999;
}
```

Добавьте в JavaScript:
```javascript
const themeToggle = document.getElementById('themeToggle');
const html = document.documentElement;

themeToggle.addEventListener('click', () => {
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    themeToggle.textContent = newTheme === 'dark' ? '☀️' : '🌙';
});

// Восстанавливаем тему при загрузке
const savedTheme = localStorage.getItem('theme') || 'light';
html.setAttribute('data-theme', savedTheme);
themeToggle.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
```

### 2. Добавьте Модальное Окно

```html
<div id="contactModal" class="modal">
    <div class="modal-content">
        <span class="close">&times;</span>
        <h2>Связаться с нами</h2>
        <form class="contact-form">
            <!-- Форма здесь -->
        </form>
    </div>
</div>
```

CSS:
```css
.modal {
    display: none;
    position: fixed;
    z-index: 2000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    animation: fadeIn 0.3s ease;
}

.modal-content {
    background: var(--white);
    margin: 10% auto;
    padding: 40px;
    border-radius: 15px;
    width: 90%;
    max-width: 500px;
    animation: slideUp 0.3s ease;
}

.close {
    float: right;
    font-size: 28px;
    font-weight: bold;
    cursor: pointer;
}
```

JavaScript:
```javascript
const modal = document.getElementById('contactModal');
const closeBtn = document.querySelector('.close');

document.querySelector('.cta-button').addEventListener('click', () => {
    modal.style.display = 'block';
});

closeBtn.addEventListener('click', () => {
    modal.style.display = 'none';
});
```

### 3. Добавьте Слайдер/Карусель

```html
<section class="testimonials">
    <div class="container">
        <h2 class="section-title">Отзывы</h2>
        <div class="slider">
            <div class="slide">
                <p>"Отличный сервис!"</p>
                <span>- Клиент 1</span>
            </div>
            <div class="slide">
                <p>"Рекомендую всем!"</p>
                <span>- Клиент 2</span>
            </div>
        </div>
        <button class="slider-btn prev">❮</button>
        <button class="slider-btn next">❯</button>
    </div>
</section>
```

CSS:
```css
.slider {
    position: relative;
    overflow: hidden;
}

.slide {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 40px;
    border-radius: 15px;
    text-align: center;
    min-height: 200px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.slide p {
    font-size: 24px;
    margin-bottom: 20px;
}

.slider-btn {
    position: absolute;
    top: 50%;
    background: var(--primary);
    border: none;
    color: white;
    cursor: pointer;
    padding: 15px;
    border-radius: 50%;
    font-size: 20px;
    z-index: 100;
}

.slider-btn.prev {
    left: 10px;
}

.slider-btn.next {
    right: 10px;
}
```

JavaScript:
```javascript
let currentSlide = 0;
const slides = document.querySelectorAll('.slide');

function showSlide(n) {
    slides.forEach(slide => slide.style.display = 'none');
    slides[n].style.display = 'block';
}

document.querySelector('.slider-btn.next').addEventListener('click', () => {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
});

document.querySelector('.slider-btn.prev').addEventListener('click', () => {
    currentSlide = (currentSlide - 1 + slides.length) % slides.length;
    showSlide(currentSlide);
});

showSlide(0);
```

## Дополнительные Советы

1. **Используйте Google Fonts** для лучших шрифтов:
```html
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
```

2. **Добавьте Smooth Scroll Behavior**:
```css
html {
    scroll-behavior: smooth;
}
```

3. **Используйте CSS Grid для адаптивности**:
```css
display: grid;
grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
```

4. **Оптимизируйте изображения**:
- Сжимайте на tinypng.com
- Используйте WebP формат
- Установите width и height атрибуты

---

**Приятного редактирования!** ✨

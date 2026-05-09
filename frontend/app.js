const API_BASE = '/api';
let token = null;

function setToken(t) { token = t; localStorage.setItem('access_token', t); }
function getToken() { return token || localStorage.getItem('access_token'); }

async function fetchJson(url, options = {}) {
    const headers = { 'Content-Type': 'application/json', ...options.headers };
    if (getToken()) headers['Authorization'] = `Bearer ${getToken()}`;
    const res = await fetch(url, { ...options, headers });
    if (res.status === 401 && !window.location.pathname.includes('login')) {
        localStorage.removeItem('access_token');
        window.location.href = 'login.html';
        return;
    }
    if (!res.ok) throw new Error(await res.text());
    return res.json();
}

// ---------- Favorites localStorage ----------
function getFavorites() {
    const fav = localStorage.getItem('favorites');
    return fav ? JSON.parse(fav) : [];
}

function saveFavorites(favs) {
    localStorage.setItem('favorites', JSON.stringify(favs));
}

function addFavorite(exId) {
    let favs = getFavorites();
    if (!favs.includes(exId)) {
        favs.push(exId);
        saveFavorites(favs);
    }
}

function removeFavorite(exId) {
    let favs = getFavorites();
    favs = favs.filter(id => id != exId);
    saveFavorites(favs);
}

function isFavorite(exId) {
    return getFavorites().includes(exId);
}

// ---------- Кнопка Войти/Выйти ----------
function updateAuthButton() {
    const authContainer = document.getElementById('authButton');
    if (!authContainer) return;
    if (getToken()) {
        authContainer.innerHTML = '<button id="logoutBtn" style="background:none; border:none; color:white; cursor:pointer;">Выйти</button>';
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.onclick = () => {
                localStorage.removeItem('access_token');
                window.location.href = 'login.html';
            };
        }
    } else {
        authContainer.innerHTML = '<a href="login.html" style="color:white; text-decoration:none;">Войти</a>';
    }
}

// Вызываем обновление кнопки после загрузки каждой страницы
document.addEventListener('DOMContentLoaded', updateAuthButton);
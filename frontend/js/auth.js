// frontend/js/auth.js
// Gestión de autenticación en el frontend

const API_URL = 'http://localhost:8000/api/v1';

// Obtener el token de autenticación
function getAuthToken() {
    return localStorage.getItem('access_token');
}

// Obtener usuario actual
function getCurrentUser() {
    const userStr = localStorage.getItem('usuario');
    if (!userStr) return null;
    try {
        return JSON.parse(userStr);
    } catch {
        return null;
    }
}

// Verificar si está autenticado
function isAuthenticated() {
    return getAuthToken() !== null;
}

// Verificar si tiene un rol específico
function hasRole(rol) {
    const user = getCurrentUser();
    if (!user) return false;
    if (user.rol === 'admin') return true; // Admin tiene todos los permisos
    return user.rol === rol;
}

// Verificar si tiene alguno de los roles
function hasAnyRole(roles) {
    const user = getCurrentUser();
    if (!user) return false;
    if (user.rol === 'admin') return true;
    return roles.includes(user.rol);
}

// Cerrar sesión
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('usuario');
    window.location.href = 'login.html';
}

// Función para hacer fetch con autenticación
async function authFetch(endpoint, options = {}) {
    const token = getAuthToken();
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers
    });
    
    // Si no está autorizado, redirigir al login
    if (response.status === 401) {
        logout();
        throw new Error('Sesión expirada');
    }
    
    return response;
}

// Verificar autenticación al cargar una página (excepto login)
function checkAuth() {
    if (!isAuthenticated() && !window.location.pathname.includes('login.html')) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

// Mostrar nombre de usuario en el sidebar
function updateUserInfo() {
    const user = getCurrentUser();
    if (user) {
        const userInfoElements = document.querySelectorAll('.user-info span, .user-name');
        userInfoElements.forEach(el => {
            if (el.classList?.contains('user-name') || el.parentElement?.classList?.contains('user-info')) {
                el.textContent = `${user.nombre} ${user.apellidos}`;
            }
        });
        
        // Mostrar rol
        const roleElements = document.querySelectorAll('.user-role');
        const rolesMap = {
            'admin': 'Administrador',
            'maestro': 'Maestro',
            'recepcion': 'Recepción',
            'caja': 'Caja',
            'invitado': 'Invitado'
        };
        roleElements.forEach(el => {
            el.textContent = rolesMap[user.rol] || user.rol;
        });
    }
}

// Ocultar elementos según rol
function applyRolePermissions() {
    const user = getCurrentUser();
    if (!user) return;
    
    // Ocultar elementos que no debe ver según su rol
    const adminOnly = document.querySelectorAll('.admin-only');
    const maestroOnly = document.querySelectorAll('.maestro-only');
    const recepcionOnly = document.querySelectorAll('.recepcion-only');
    
    if (user.rol === 'admin') {
        adminOnly.forEach(el => el.style.display = '');
        maestroOnly.forEach(el => el.style.display = '');
        recepcionOnly.forEach(el => el.style.display = '');
    } else if (user.rol === 'maestro') {
        adminOnly.forEach(el => el.style.display = 'none');
        maestroOnly.forEach(el => el.style.display = '');
        recepcionOnly.forEach(el => el.style.display = '');
    } else if (user.rol === 'recepcion') {
        adminOnly.forEach(el => el.style.display = 'none');
        maestroOnly.forEach(el => el.style.display = 'none');
        recepcionOnly.forEach(el => el.style.display = '');
    } else {
        adminOnly.forEach(el => el.style.display = 'none');
        maestroOnly.forEach(el => el.style.display = 'none');
        recepcionOnly.forEach(el => el.style.display = 'none');
    }
}

// Botón de cerrar sesión
function setupLogoutButton() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }
}

// Inicializar autenticación
document.addEventListener('DOMContentLoaded', () => {
    if (checkAuth()) {
        updateUserInfo();
        applyRolePermissions();
        setupLogoutButton();
    }
});
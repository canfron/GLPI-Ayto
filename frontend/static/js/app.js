// app.js

let currentUser = null;
let apiToken = localStorage.getItem('apiToken');

// Elementos DOM
const loginContainer = document.getElementById('login-container');
const appContainer = document.getElementById('app-container');
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const btnLogout = document.getElementById('btn-logout');
const displayUsername = document.getElementById('display-username');

// Navegación
const navItems = document.querySelectorAll('.nav-item');
const views = document.querySelectorAll('.view-section');
const viewTitle = document.getElementById('view-title');
const navTechPanel = document.getElementById('nav-tech-panel');

// Modal
const modalTicket = document.getElementById('modal-ticket');
const btnNewTicket = document.getElementById('btn-new-ticket');
const closeModals = document.querySelectorAll('.close-modal');
const categorySelect = document.getElementById('ticket-category');
const newTicketForm = document.getElementById('new-ticket-form');

// API helpers
async function apiFetch(url, options = {}) {
    const headers = { 'Content-Type': 'application/json' };
    if (apiToken) { headers['Authorization'] = `Bearer ${apiToken}`; }
    
    // Anexar access_token como query param temporalmente hasta usar tokens reales JWT
    let finalUrl = url;
    if (apiToken && !options.method || options.method === 'GET') {
        const joiner = url.includes('?') ? '&' : '?';
        finalUrl += `${joiner}access_token=${encodeURIComponent(apiToken)}`;
    }

    try {
        const res = await fetch(finalUrl, { ...options, headers });
        if (res.status === 401) { logout(); throw new Error('No autorizado'); }
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Error en petición');
        return data;
    } catch(err) {
        console.error(err);
        throw err;
    }
}

// Auth
async function checkAuth() {
    if (!apiToken) { showLogin(); return; }
    try {
        currentUser = await apiFetch('/api/users/me');
        initApp();
    } catch(err) {
        logout();
    }
}

async function login(username, password) {
    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Error de login');
        
        apiToken = data.access_token;
        localStorage.setItem('apiToken', apiToken);
        await checkAuth();
    } catch(err) {
        loginError.textContent = err.message;
    }
}

function logout() {
    apiToken = null;
    currentUser = null;
    localStorage.removeItem('apiToken');
    showLogin();
}

function showLogin() {
    appContainer.classList.add('hidden');
    loginContainer.classList.remove('hidden');
}

function initApp() {
    loginContainer.classList.add('hidden');
    appContainer.classList.remove('hidden');
    displayUsername.textContent = currentUser.username;
    
    // Mostrar panel técnico si es rol 1 o 2
    if (currentUser.role_id === 1 || currentUser.role_id === 2) {
        navTechPanel.classList.remove('hidden');
    } else {
        navTechPanel.classList.add('hidden');
    }

    loadCategories();
    loadDashboard();
}

// Navegación
navItems.forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        const view = e.currentTarget.dataset.view;
        
        navItems.forEach(n => n.classList.remove('active'));
        e.currentTarget.classList.add('active');

        views.forEach(v => v.classList.add('hidden'));
        document.getElementById(`view-${view}`).classList.remove('hidden');
        
        viewTitle.textContent = e.currentTarget.textContent.trim();

        if (view === 'tickets') loadTickets();
    });
});

// Modal Nuevo Ticket
btnNewTicket.addEventListener('click', () => modalTicket.classList.remove('hidden'));
closeModals.forEach(btn => btn.addEventListener('click', () => modalTicket.classList.add('hidden')));

// Cargar Datos
async function loadCategories() {
    try {
        // En un entorno real se pediria ?all=true solo si es tecnico (1 o 2)
        const isTech = currentUser.role_id === 1 || currentUser.role_id === 2;
        const cats = await apiFetch(`/api/categories?all=${isTech}`);
        
        categorySelect.innerHTML = '<option value="">Seleccione una opción...</option>';
        cats.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.id;
            // Para UI, podríamos indentar por parent_id, por ahora listamos
            opt.textContent = (c.parent_id ? "— " : "") + c.name;
            categorySelect.appendChild(opt);
        });
    } catch(e) { console.error('Error cargando categorias', e); }
}

async function loadTickets() {
    try {
        const tbody = document.getElementById('tickets-tbody');
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center">Cargando...</td></tr>';
        
        // Petición POST para mandar token en query u otro lado
        const tickets = await apiFetch(`/api/tickets`);
        
        // Filtrar si es usuario normal
        const misTickets = currentUser.role_id === 3 
            ? tickets.filter(t => t.requester_id === currentUser.id)
            : tickets;

        tbody.innerHTML = '';
        if(misTickets.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center">No hay tickets</td></tr>';
            return;
        }

        misTickets.forEach(t => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>#${t.id}</td>
                <td><strong>${t.title}</strong></td>
                <td>${t.category_id}</td>
                <td><span class="badge ${t.status.replace(' ', '_')}">${t.status}</span></td>
                <td>${t.priority}</td>
                <td>${new Date(t.created_at).toLocaleDateString()}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch(e) { console.error('Error cargando tickets', e); }
}

async function loadDashboard() {} // En dashboard podríamos calcular stats

// Eventos
loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    loginError.textContent = '';
    const u = document.getElementById('username').value;
    const p = document.getElementById('password').value;
    login(u, p);
});

btnLogout.addEventListener('click', logout);

newTicketForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        title: document.getElementById('ticket-title').value,
        category_id: parseInt(document.getElementById('ticket-category').value),
        description: document.getElementById('ticket-desc').value,
        priority: 'Media'
    };

    try {
        await fetch(`/api/tickets?access_token=${encodeURIComponent(apiToken)}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        modalTicket.classList.add('hidden');
        newTicketForm.reset();
        
        // Refrescar
        if(!document.getElementById('view-tickets').classList.contains('hidden')) {
            loadTickets();
        } else {
            alert('Incidencia registrada.');
        }
    } catch(err) { alert('Error creando ticket'); }
});

// Init
checkAuth();

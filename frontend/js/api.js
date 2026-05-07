// frontend/js/api.js
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Función genérica para llamadas a la API
// frontend/js/api.js - Modificar apiCall para usar token

async function apiCall(endpoint, method = 'GET', data = null) {
    const token = localStorage.getItem('access_token');
    
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    };
    
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        
        if (response.status === 401) {
            // Token expirado o inválido
            localStorage.removeItem('access_token');
            localStorage.removeItem('usuario');
            window.location.href = '/login.html';
            throw new Error('Sesión expirada');
        }
        
        if (!response.ok) {
            let errorMessage = `Error ${response.status}: ${response.statusText}`;
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    errorMessage = errorData.detail;
                }
            } catch (e) {}
            throw new Error(errorMessage);
        }
        
        const text = await response.text();
        if (!text) return null;
        return JSON.parse(text);
    } catch (error) {
        console.error(`API Error: ${method} ${endpoint}`, error);
        throw error;
    }
}

// Alumnos
async function getAlumnos(params = '') {
    return await apiCall(`/alumnos/${params}`);
}

async function getAlumno(id) {
    return await apiCall(`/alumnos/${id}`);
}

async function createAlumno(data) {
    return await apiCall('/alumnos/', 'POST', data);
}

async function updateAlumno(id, data) {
    return await apiCall(`/alumnos/${id}`, 'PUT', data);
}

async function updateExpediente(id, data) {
    return await apiCall(`/alumnos/${id}/expediente`, 'PUT', data);
}

async function registrarAscenso(id, data) {
    return await apiCall(`/alumnos/${id}/ascender`, 'POST', data);
}

async function registrarLogro(id, data) {
    return await apiCall(`/alumnos/${id}/logros`, 'POST', data);
}

async function marcarAsistencia(id) {
    return await apiCall(`/alumnos/${id}/asistencia`, 'PUT');
}

async function pagarMensualidad(id) {
    return await apiCall(`/alumnos/${id}/pagar-mensualidad`, 'PUT');
}



// Eventos
async function getEventos() {
    return await apiCall('/eventos/');
}

async function getEventosProximos() {
    return await apiCall('/eventos/proximos');
}

async function createEvento(data) {
    return await apiCall('/eventos/', 'POST', data);
}

async function inscribirEvento(eventoId, alumnoId, data) {
    return await apiCall(`/eventos/${eventoId}/inscribir?alumno_id=${alumnoId}`, 'POST', data);
}

// Horarios
async function getHorarios() {
    return await apiCall('/horarios/');
}

async function getHorariosHoy() {
    return await apiCall('/horarios/hoy');
}

async function createHorario(data) {
    console.log('Enviando datos al backend:', data); // Para depuración
    const result = await apiCall('/horarios/', 'POST', data);
    console.log('Respuesta del backend:', result);
    return result;
}


async function inscribirClase(horarioId, alumnoId, data) {
    return await apiCall(`/horarios/${horarioId}/inscribir?alumno_id=${alumnoId}`, 'POST', data);
}

// Asistencias
async function tomarLista(data) {
    return await apiCall('/asistencias/tomar-lista', 'POST', data);
}

async function getAsistenciasAlumno(alumnoId) {
    return await apiCall(`/asistencias/alumno/${alumnoId}`);
}

// Dashboard y Reportes
async function getDashboardResumen() {
    return await apiCall('/dashboard/resumen');
}

async function getDashboardAlertas() {
    return await apiCall('/dashboard/alertas');
}

async function getTendencias(meses = 6) {
    return await apiCall(`/dashboard/tendencias?meses=${meses}`);
}

async function getMedallero() {
    return await apiCall('/reportes/rendimiento/medallero');
}

async function getTopAsistencia() {
    return await apiCall('/reportes/asistencia/top-alumnos');
}

async function getHistorialPesos(alumnoId) {
    return await apiCall(`/alumnos/${alumnoId}/historial-pesos`);
}

// Obtener historial de grados
async function getHistorialGrados(alumnoId) {
    return await apiCall(`/alumnos/${alumnoId}/historial-grados`);
}

// Obtener técnicas del alumno
async function getTecnicasAlumno(alumnoId) {
    return await apiCall(`/alumnos/${alumnoId}/tecnicas`);
}

// Agregar técnica
async function addTecnica(alumnoId, data) {
    return await apiCall(`/alumnos/${alumnoId}/tecnicas`, 'POST', data);
}

// Actualizar alumno completo
async function updateAlumnoCompleto(alumnoId, data) {
    return await apiCall(`/alumnos/${alumnoId}`, 'PUT', data);
}

// Registrar peso
async function registrarPeso(alumnoId, data) {
    return await apiCall(`/alumnos/${alumnoId}/peso`, 'POST', data);
}

// Registrar ascenso
async function registrarAscenso(alumnoId, data) {
    return await apiCall(`/alumnos/${alumnoId}/ascender`, 'POST', data);
}

// Obtener inscripciones del alumno a clases
async function getInscripcionesAlumno(alumnoId) {
    return await apiCall(`/alumnos/${alumnoId}/inscripciones-clase`);
}

// ==================== HORARIOS ====================

// Obtener todos los horarios
async function getHorarios() {
    return await apiCall('/horarios/');
}

// Crear nuevo horario
async function createHorario(data) {
    return await apiCall('/horarios/', 'POST', data);
}

// Actualizar horario
async function updateHorario(id, data) {
    return await apiCall(`/horarios/${id}`, 'PUT', data);
}

// Obtener inscripciones por horario
async function getInscripcionesPorHorario(horarioId) {
    return await apiCall(`/horarios/${horarioId}/inscritos`);
}

// Obtener inscripciones del alumno
async function getInscripcionesAlumno(alumnoId) {
    return await apiCall(`/alumnos/${alumnoId}/inscripciones-clase`);
}

// Inscribir alumno a clase
async function inscribirClase(horarioId, alumnoId, data = {}) {
    return await apiCall(`/horarios/${horarioId}/inscribir?alumno_id=${alumnoId}`, 'POST', data);
}

// Tomar lista de asistencia
async function tomarLista(data) {
    return await apiCall('/asistencias/tomar-lista', 'POST', data);
}

// Obtener asistencia por horario y fecha
async function getAsistenciasPorHorario(horarioId, fecha) {
    return await apiCall(`/asistencias/clase/${horarioId}?fecha=${fecha}`);
}

// ==================== EVENTOS ====================

// Obtener todos los eventos
async function getEventos() {
    return await apiCall('/eventos/');
}

// Obtener eventos próximos
async function getEventosProximos() {
    return await apiCall('/eventos/proximos');
}

// Crear evento
async function createEvento(data) {
    return await apiCall('/eventos/', 'POST', data);
}

// Obtener inscritos de un evento
async function getInscritosEvento(eventoId) {
    return await apiCall(`/eventos/${eventoId}/inscritos`);
}

// Inscribir alumno a evento
async function inscribirEvento(eventoId, alumnoId, data) {
    return await apiCall(`/eventos/${eventoId}/inscribir?alumno_id=${alumnoId}`, 'POST', data);
}

// Obtener un evento específico
async function getEvento(eventoId) {
    return await apiCall(`/eventos/${eventoId}`);
}

// Actualizar evento
async function updateEvento(eventoId, data) {
    return await apiCall(`/eventos/${eventoId}`, 'PUT', data);
}

// Eliminar evento (hard delete)
async function deleteEvento(eventoId) {
    return await apiCall(`/eventos/${eventoId}`, 'DELETE');
}

// Confirmar pago de inscripción
async function confirmarPagoInscripcion(inscripcionId) {
    return await apiCall(`/eventos/inscripciones/${inscripcionId}/pagar`, 'PUT');
}

// Maestros
async function getMaestros() {
    return await apiCall('/maestros/');
}

async function createMaestro(data) {
    return await apiCall('/maestros/', 'POST', data);
}

// Obtener un maestro específico
async function getMaestro(maestroId) {
    return await apiCall(`/maestros/${maestroId}`);
}

// Actualizar maestro
async function updateMaestro(maestroId, data) {
    return await apiCall(`/maestros/${maestroId}`, 'PUT', data);
}
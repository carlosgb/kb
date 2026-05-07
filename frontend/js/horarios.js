// frontend/js/horarios.js
// Funciones para la gestión de horarios y clases

const diasSemana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
let horariosData = [];
let maestrosData = [];
let alumnosData = [];
let horarioSeleccionado = null;
let alumnosInscritos = [];

// Cargar horarios por día
async function cargarHorarios() {
    try {
        horariosData = await getHorarios();
        await cargarMaestros();
        await cargarAlumnosLista();
        renderDiasTabs();
        
        const diaActual = new Date().getDay();
        const diaIndex = diaActual === 0 ? 6 : diaActual - 1;
        cargarHorariosPorDia(diaIndex);
    } catch (error) {
        console.error('Error cargando horarios:', error);
        document.getElementById('horariosGrid').innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-circle"></i><p>Error cargando horarios</p></div>';
    }
}

// Cargar maestros
async function cargarMaestros() {
    try {
        maestrosData = await getMaestros();
        
        // Llenar selects de maestros
        const selects = ['new_maestro', 'edit_maestro'];
        for (const selectId of selects) {
            const select = document.getElementById(selectId);
            if (select) {
                select.innerHTML = '<option value="">Seleccionar profesor</option>' +
                    maestrosData.filter(m => m.activo).map(m => 
                        `<option value="${m.id}">${m.nombre} ${m.apellidos} - ${m.especialidad || 'General'}</option>`
                    ).join('');
            }
        }
    } catch (error) {
        console.error('Error cargando maestros:', error);
    }
}

// Cargar lista de alumnos para inscripciones
async function cargarAlumnosLista() {
    try {
        alumnosData = await getAlumnos('?activo=true');
    } catch (error) {
        console.error('Error cargando alumnos:', error);
    }
}

// Renderizar tabs de días
function renderDiasTabs() {
    const container = document.getElementById('diasTabs');
    const hoy = new Date().getDay();
    const diaActual = hoy === 0 ? 6 : hoy - 1;
    
    container.innerHTML = diasSemana.map((dia, idx) => `
        <button class="dia-tab ${idx === diaActual ? 'active' : ''}" onclick="cargarHorariosPorDia(${idx})">
            ${dia}
        </button>
    `).join('');
}

// Cargar horarios por día específico
async function cargarHorariosPorDia(dia) {
    document.querySelectorAll('.dia-tab').forEach((tab, i) => {
        if (i === dia) tab.classList.add('active');
        else tab.classList.remove('active');
    });
    
    const horariosFiltrados = horariosData.filter(h => h.dia_semana === dia);
    renderHorarios(horariosFiltrados);
}

// Renderizar tarjetas de horarios
function renderHorarios(horarios) {
    const container = document.getElementById('horariosGrid');
    
    if (!horarios || horarios.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-calendar-day"></i>
                <p>No hay clases programadas para este día</p>
                <button class="btn-primary" style="margin-top: 15px;" onclick="abrirModalNuevoHorario()">
                    <i class="fas fa-plus"></i> Agregar Clase
                </button>
            </div>
        `;
        return;
    }
    
    container.innerHTML = horarios.map(horario => {
        const maestro = maestrosData.find(m => m.id === horario.maestro_id);
        const porcentaje = (horario.alumnos_inscritos / horario.capacidad_maxima) * 100;
        const estaLleno = horario.alumnos_inscritos >= horario.capacidad_maxima;
        
        return `
            <div class="horario-card">
                <div class="horario-header">
                    <div class="horario-titulo">
                        <h3><i class="fas fa-fist-raised"></i> ${horario.nombre}</h3>
                        <p>${horario.tipo_clase} • ${horario.nivel}</p>
                    </div>
                    <span class="badge ${horario.activo ? 'activo' : 'inactivo'}">
                        ${horario.activo ? 'Activo' : 'Inactivo'}
                    </span>
                </div>
                <div class="horario-body">
                    <div class="horario-info">
                        <div class="info-row">
                            <span><i class="fas fa-clock"></i> Horario</span>
                            <span>${horario.hora_inicio} - ${horario.hora_fin}</span>
                        </div>
                        <div class="info-row">
                            <span><i class="fas fa-chalkboard-user"></i> Profesor</span>
                            <span>${maestro ? `${maestro.nombre} ${maestro.apellidos}` : 'No asignado'}</span>
                        </div>
                        <div class="info-row">
                            <span><i class="fas fa-door-open"></i> Salón</span>
                            <span>${horario.salon || 'Principal'}</span>
                        </div>
                        <div class="info-row">
                            <span><i class="fas fa-users"></i> Cupo</span>
                            <span><strong>${horario.alumnos_inscritos}</strong> / ${horario.capacidad_maxima}</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${porcentaje}%"></div>
                        </div>
                    </div>
                    <div class="horario-actions">
                        <button class="btn-asistencia" onclick="abrirModalAsistencia(${horario.id}, '${horario.nombre}')" title="Tomar Asistencia">
                            <i class="fas fa-check-circle"></i> Lista
                        </button>
                        <button class="btn-inscribir" onclick="abrirModalInscribir(${horario.id}, '${horario.nombre}')" title="Inscribir Alumno" ${estaLleno ? 'disabled style="opacity:0.5;"' : ''}>
                            <i class="fas fa-user-plus"></i> Inscribir
                        </button>
                        <button class="btn-editar" onclick="editarHorario(${horario.id})" title="Editar Clase">
                            <i class="fas fa-edit"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Abrir modal nuevo horario
function abrirModalNuevoHorario() {
    document.getElementById('formNuevoHorario').reset();
    document.getElementById('new_capacidad').value = '20';
    document.getElementById('new_salon').value = 'Principal';
    document.getElementById('new_activo').checked = true;
    document.getElementById('modalNuevoHorario').style.display = 'flex';
}

// Guardar nuevo horario
async function guardarNuevoHorario() {
    // Validar campos requeridos
    const nombre = document.getElementById('new_nombre').value;
    const horaInicio = document.getElementById('new_hora_inicio').value;
    const horaFin = document.getElementById('new_hora_fin').value;
    
    if (!nombre) {
        alert('❌ Por favor ingrese el nombre de la clase');
        return;
    }
    
    if (!horaInicio || !horaFin) {
        alert('❌ Por favor ingrese la hora de inicio y fin');
        return;
    }
    
    if (horaInicio >= horaFin) {
        alert('❌ La hora de fin debe ser mayor a la hora de inicio');
        return;
    }
    
    // Construir datos
    const data = {
        nombre: nombre,
        tipo_clase: document.getElementById('new_tipo').value,
        nivel: document.getElementById('new_nivel').value,
        dia_semana: parseInt(document.getElementById('new_dia').value),
        hora_inicio: horaInicio,
        hora_fin: horaFin,
        capacidad_maxima: parseInt(document.getElementById('new_capacidad').value) || 20,
        salon: document.getElementById('new_salon').value || 'Principal',
        activo: document.getElementById('new_activo').checked
    };
    
    // Agregar maestro solo si se seleccionó
    const maestroId = document.getElementById('new_maestro').value;
    if (maestroId) {
        data.maestro_id = parseInt(maestroId);
    }
    
    console.log('Datos a enviar:', JSON.stringify(data, null, 2));
    
    // Mostrar loading
    const btnSubmit = document.querySelector('#formNuevoHorario button[type="submit"]');
    const originalText = btnSubmit.innerHTML;
    btnSubmit.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creando...';
    btnSubmit.disabled = true;
    
    try {
        const resultado = await createHorario(data);
        console.log('Resultado:', resultado);
        alert('✅ Clase creada correctamente');
        cerrarModalNuevoHorario();
        cargarHorarios();
    } catch (error) {
        console.error('Error completo:', error);
        alert('❌ Error: ' + (error.message || 'Error desconocido'));
    } finally {
        btnSubmit.innerHTML = originalText;
        btnSubmit.disabled = false;
    }
}

// Función para calcular duración en minutos
function calcularDuracion(horaInicio, horaFin) {
    const [h1, m1] = horaInicio.split(':').map(Number);
    const [h2, m2] = horaFin.split(':').map(Number);
    let minutos = (h2 * 60 + m2) - (h1 * 60 + m1);
    if (minutos < 0) minutos += 24 * 60;
    return minutos;
}

// Editar horario
async function editarHorario(id) {
    const horario = horariosData.find(h => h.id === id);
    if (!horario) return;
    
    document.getElementById('edit_id').value = horario.id;
    document.getElementById('edit_nombre').value = horario.nombre;
    document.getElementById('edit_tipo').value = horario.tipo_clase;
    document.getElementById('edit_nivel').value = horario.nivel;
    document.getElementById('edit_dia').value = horario.dia_semana;
    document.getElementById('edit_hora_inicio').value = horario.hora_inicio;
    document.getElementById('edit_hora_fin').value = horario.hora_fin;
    document.getElementById('edit_capacidad').value = horario.capacidad_maxima;
    document.getElementById('edit_salon').value = horario.salon || 'Principal';
    document.getElementById('edit_maestro').value = horario.maestro_id || '';
    document.getElementById('edit_activo').checked = horario.activo;
    
    document.getElementById('modalEditarHorario').style.display = 'flex';
}

// Guardar edición de horario
async function guardarEditarHorario() {
    const id = document.getElementById('edit_id').value;
    const data = {
        nombre: document.getElementById('edit_nombre').value,
        tipo_clase: document.getElementById('edit_tipo').value,
        nivel: document.getElementById('edit_nivel').value,
        dia_semana: parseInt(document.getElementById('edit_dia').value),
        hora_inicio: document.getElementById('edit_hora_inicio').value,
        hora_fin: document.getElementById('edit_hora_fin').value,
        capacidad_maxima: parseInt(document.getElementById('edit_capacidad').value),
        salon: document.getElementById('edit_salon').value,
        maestro_id: document.getElementById('edit_maestro').value || null,
        activo: document.getElementById('edit_activo').checked
    };
    
    try {
        await updateHorario(id, data);
        alert('✅ Clase actualizada correctamente');
        cerrarModalEditarHorario();
        cargarHorarios();
    } catch (error) {
        alert('❌ Error al actualizar clase: ' + error.message);
    }
}

// Abrir modal inscribir alumno
let horarioInscribirId = null;
function abrirModalInscribir(horarioId, horarioNombre) {
    horarioInscribirId = horarioId;
    document.getElementById('inscribirClaseNombre').value = horarioNombre;
    
    // Llenar select de alumnos
    const select = document.getElementById('inscribirAlumnoId');
    select.innerHTML = '<option value="">-- Seleccione un alumno --</option>' +
        alumnosData.filter(a => a.activo).map(a => 
            `<option value="${a.id}">${a.nombre} ${a.apellidos} - ${a.grado_actual || 'Principiante'}</option>`
        ).join('');
    
    document.getElementById('modalInscribirAlumno').style.display = 'flex';
}

// Confirmar inscripción de alumno
async function confirmarInscribirAlumno() {
    const alumnoId = document.getElementById('inscribirAlumnoId').value;
    const notas = document.getElementById('inscribirNotas').value;
    
    if (!alumnoId) {
        alert('Por favor seleccione un alumno');
        return;
    }
    
    try {
        await inscribirClase(horarioInscribirId, alumnoId, { notas: notas });
        alert('✅ Alumno inscrito correctamente');
        cerrarModalInscribir();
        cargarHorarios();
    } catch (error) {
        alert('❌ Error al inscribir alumno: ' + error.message);
    }
}

// Abrir modal tomar asistencia
let horarioAsistenciaId = null;
async function abrirModalAsistencia(horarioId, horarioNombre) {
    horarioAsistenciaId = horarioId;
    document.getElementById('asistenciaClaseNombre').value = horarioNombre;
    document.getElementById('asistenciaFecha').value = new Date().toISOString().split('T')[0];
    
    // Cargar alumnos inscritos
    await cargarAlumnosInscritos(horarioId);
    
    document.getElementById('modalAsistencia').style.display = 'flex';
}

// Cargar alumnos inscritos a la clase
async function cargarAlumnosInscritos(horarioId) {
    const container = document.getElementById('listaAlumnosAsistencia');
    container.innerHTML = '<div class="loading">Cargando alumnos...</div>';
    
    try {
        const inscripciones = await getInscripcionesPorHorario(horarioId);
        alumnosInscritos = inscripciones.filter(i => i.activo);
        
        if (alumnosInscritos.length === 0) {
            container.innerHTML = '<div class="empty-state"><p>No hay alumnos inscritos en esta clase</p></div>';
            return;
        }
        
        container.innerHTML = alumnosInscritos.map(alumno => {
            const alumnoInfo = alumnosData.find(a => a.id === alumno.alumno_id);
            return `
                <div class="alumno-item">
                    <div class="alumno-avatar">
                        ${alumnoInfo?.nombre?.charAt(0) || 'A'}
                    </div>
                    <input type="checkbox" id="asistencia_${alumno.alumno_id}" value="${alumno.alumno_id}" checked>
                    <label for="asistencia_${alumno.alumno_id}">
                        <strong>${alumnoInfo?.nombre || 'Alumno'} ${alumnoInfo?.apellidos || ''}</strong>
                        <div class="alumno-grado">${alumnoInfo?.grado_actual || 'Principiante'}</div>
                    </label>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error cargando inscritos:', error);
        container.innerHTML = '<div class="empty-state"><p>Error cargando alumnos</p></div>';
    }
}

// Guardar asistencia
async function guardarAsistencia() {
    const presentes = [];
    for (const alumno of alumnosInscritos) {
        const checkbox = document.getElementById(`asistencia_${alumno.alumno_id}`);
        if (checkbox && checkbox.checked) {
            presentes.push(alumno.alumno_id);
        }
    }
    
    const data = {
        horario_id: horarioAsistenciaId,
        fecha_clase: document.getElementById('asistenciaFecha').value,
        presentes: presentes,
        ausentes: []
    };
    
    try {
        await tomarLista(data);
        alert('✅ Asistencia guardada correctamente');
        cerrarModalAsistencia();
        cargarHorarios();
    } catch (error) {
        alert('❌ Error al guardar asistencia: ' + error.message);
    }
}

// Ver alumnos inscritos
async function verInscritos(horarioId, horarioNombre) {
    document.getElementById('verInscritosClaseNombre').value = horarioNombre;
    const container = document.getElementById('listaInscritos');
    container.innerHTML = '<div class="loading">Cargando...</div>';
    
    try {
        const inscripciones = await getInscripcionesPorHorario(horarioId);
        const inscritosActivos = inscripciones.filter(i => i.activo);
        
        if (inscritosActivos.length === 0) {
            container.innerHTML = '<div class="empty-state"><p>No hay alumnos inscritos</p></div>';
        } else {
            container.innerHTML = inscritosActivos.map(inscripcion => {
                const alumno = alumnosData.find(a => a.id === inscripcion.alumno_id);
                return `
                    <div class="alumno-item">
                        <div class="alumno-avatar">
                            ${alumno?.nombre?.charAt(0) || 'A'}
                        </div>
                        <div style="flex: 1;">
                            <strong>${alumno?.nombre || 'Alumno'} ${alumno?.apellidos || ''}</strong>
                            <div class="alumno-grado">${alumno?.grado_actual || 'Principiante'} • ${alumno?.telefono_celular || 'Sin teléfono'}</div>
                            ${inscripcion.notas ? `<div class="alumno-grado" style="color:#e94560;">Nota: ${inscripcion.notas}</div>` : ''}
                        </div>
                        <button class="btn-danger" style="padding: 5px 10px;" onclick="darBajaAlumnoClase(${inscripcion.id}, ${horarioId})">
                            <i class="fas fa-ban"></i> Dar Baja
                        </button>
                    </div>
                `;
            }).join('');
        }
        
        document.getElementById('modalVerInscritos').style.display = 'flex';
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = '<div class="empty-state"><p>Error cargando inscritos</p></div>';
    }
}

// Dar de baja alumno de clase
async function darBajaAlumnoClase(inscripcionId, horarioId) {
    if (confirm('¿Dar de baja a este alumno de la clase?')) {
        try {
            await apiCall(`/horarios/inscripciones/${inscripcionId}`, 'DELETE');
            alert('✅ Alumno dado de baja correctamente');
            cerrarModalVerInscritos();
            cargarHorarios();
        } catch (error) {
            alert('❌ Error al dar de baja: ' + error.message);
        }
    }
}

// Cerrar modales
function cerrarModalNuevoHorario() {
    document.getElementById('modalNuevoHorario').style.display = 'none';
}

function cerrarModalEditarHorario() {
    document.getElementById('modalEditarHorario').style.display = 'none';
}

function cerrarModalInscribir() {
    document.getElementById('modalInscribirAlumno').style.display = 'none';
    horarioInscribirId = null;
}

function cerrarModalAsistencia() {
    document.getElementById('modalAsistencia').style.display = 'none';
    horarioAsistenciaId = null;
}

function cerrarModalVerInscritos() {
    document.getElementById('modalVerInscritos').style.display = 'none';
}

// Filtrar alumnos en el select
function filtrarAlumnos() {
    const busqueda = document.getElementById('buscarAlumno').value.toLowerCase();
    const select = document.getElementById('inscribirAlumnoId');
    const options = select.options;
    
    for (let i = 0; i < options.length; i++) {
        const text = options[i].text.toLowerCase();
        if (text.includes(busqueda) || busqueda === '') {
            options[i].style.display = '';
        } else {
            options[i].style.display = 'none';
        }
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    cargarHorarios();
    
    const formNuevo = document.getElementById('formNuevoHorario');
    if (formNuevo) {
        formNuevo.addEventListener('submit', (e) => {
            e.preventDefault();
            guardarNuevoHorario();
        });
    }
    
    const formEditar = document.getElementById('formEditarHorario');
    if (formEditar) {
        formEditar.addEventListener('submit', (e) => {
            e.preventDefault();
            guardarEditarHorario();
        });
    }
});
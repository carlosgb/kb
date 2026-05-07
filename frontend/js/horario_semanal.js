// horario_semanal.js - Versión completa con creación, edición y detalle de clases

let horariosGlobal = [];
let maestrosGlobal = [];
let claseSeleccionadaGlobal = null;

const diasSemana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
const iconosPorTipo = {
    'K1': '🥊',
    'Kick Light': '🦵',
    'Point Fighting': '🎯',
    'Acondicionamiento': '💪',
    'Infantil': '👶',
    'Full Contact': '🥋'
};

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM cargado, iniciando...");
    cargarHorarioSemanal();
    
    // Configurar el formulario de nueva clase
    const formNuevo = document.getElementById('formNuevoHorario');
    if (formNuevo) {
        formNuevo.addEventListener('submit', guardarNuevaClase);
    }
    
    // Configurar formulario de edición
    const formEditar = document.getElementById('formEditarHorario');
    if (formEditar) {
        formEditar.addEventListener('submit', guardarEditarClase);
    }
});

// ==================== CARGAR HORARIO ====================

async function cargarHorarioSemanal() {
    const container = document.getElementById('tablaContainer');
    if (!container) {
        console.error('No existe tablaContainer');
        return;
    }
    
    container.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Cargando horario...</div>';
    
    try {
        const token = localStorage.getItem('access_token');
        if (!token) {
            window.location.href = 'login.html';
            return;
        }
        
        const [horariosRes, maestrosRes] = await Promise.all([
            fetch('http://localhost:8000/api/v1/horarios/', {
                headers: { 'Authorization': `Bearer ${token}` }
            }),
            fetch('http://localhost:8000/api/v1/maestros/', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
        ]);
        
        if (!horariosRes.ok) throw new Error('Error al cargar horarios');
        
        horariosGlobal = await horariosRes.json();
        maestrosGlobal = await maestrosRes.json();
        
        console.log('Horarios cargados:', horariosGlobal.length);
        
        construirTablaSemanal();
        
        // Cargar maestros en los selects
        cargarMaestrosEnSelect();
        
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = '<div class="empty-state">Error cargando horarios</div>';
    }
}

// ==================== CONSTRUIR TABLA ====================

function construirTablaSemanal() {
    // Obtener horas únicas

   
    const horasSet = new Set();
    horariosGlobal.forEach(h => {
        if (h.activo !== false) {
            horasSet.add(h.hora_inicio.substring(0, 5));
        }
    });
    
    let horas = Array.from(horasSet).sort();
    
    if (horas.length === 0) {
        document.getElementById('tablaContainer').innerHTML = `
            <div class="empty-state">
                <i class="fas fa-calendar-alt"></i>
                <p>No hay horarios creados</p>
                <button class="btn-primary" onclick="abrirModalNuevoHorario()">Crear Primera Clase</button>
            </div>
        `;
        return;
    }
    
    const tabla = document.createElement('table');
    tabla.className = 'horario-semanal';
    tabla.style.width = '100%';
    tabla.style.borderCollapse = 'collapse';
    tabla.style.border = '1px solid #eef2f6';
    
    // Cabecera
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    headerRow.innerHTML = `<th style="padding:12px; background:#f8f9fa; border:1px solid #eef2f6;">Hora</th>${
        diasSemana.map(d => `<th style="padding:12px; background:#f8f9fa; border:1px solid #eef2f6;">${d}</th>`).join('')
    }`;
    thead.appendChild(headerRow);
    tabla.appendChild(thead);
    
    // Cuerpo
    const tbody = document.createElement('tbody');
    
    horas.forEach(hora => {
        const fila = document.createElement('tr');
        
        // Celda hora
        const tdHora = document.createElement('td');
        tdHora.textContent = hora;
        tdHora.style.padding = '12px';
        tdHora.style.border = '1px solid #eef2f6';
        tdHora.style.fontWeight = 'bold';
        tdHora.style.background = '#f8f9fa';
        tdHora.style.textAlign = 'center';
        fila.appendChild(tdHora);
        
        // Celdas por día
        for (let i = 0; i < 7; i++) {
            const celda = document.createElement('td');
            celda.style.padding = '8px';
            celda.style.border = '1px solid #eef2f6';
            celda.style.verticalAlign = 'top';
            celda.style.minWidth = '130px';
            
            const clase = horariosGlobal.find(h => 
                h.dia_semana === i && 
                h.hora_inicio.substring(0, 5) === hora && 
                h.activo !== false
            );
            
            if (clase) {
                const maestro = maestrosGlobal.find(m => m.id === clase.maestro_id);
                const icono = iconosPorTipo[clase.tipo_clase] || '🥋';
                const inscritos = clase.alumnos_inscritos || 0;
                const capacidad = clase.capacidad_maxima || 20;
                const porcentaje = Math.round((inscritos / capacidad) * 100);
                
                let colorCupo = '#10b981';
                if (porcentaje >= 90) colorCupo = '#ef4444';
                else if (porcentaje >= 70) colorCupo = '#f59e0b';
                
                celda.innerHTML = `
                    <div class="clase-cell" onclick="verDetalleClase(${clase.id})" style="cursor:pointer; background:#fff5f7; padding:10px; border-radius:12px; transition:all 0.2s;">
                        <div style="font-weight:bold; color:#e94560; font-size:14px;">${icono} ${clase.nombre}</div>
                        <div style="font-size:11px; color:#666; margin:4px 0;">${clase.hora_inicio} - ${clase.hora_fin}</div>
                        <div style="font-size:10px; color:#999;">👨‍🏫 ${maestro ? maestro.nombre.split(' ')[0] : 'Sin profe'}</div>
                        <div style="font-size:10px; margin-top:5px;">
                            <span style="color:${colorCupo};">👥 ${inscritos}/${capacidad}</span>
                            <span style="margin-left:8px;">📊 ${porcentaje}%</span>
                        </div>
                    </div>
                `;
            } else {
                celda.innerHTML = '<div style="color:#ccc; text-align:center; padding:15px 5px;">—</div>';
            }
            
            fila.appendChild(celda);
        }
        
        tbody.appendChild(fila);
    });
    
    tabla.appendChild(tbody);
    
    const container = document.getElementById('tablaContainer');
    container.innerHTML = '';
    container.appendChild(tabla);
}

// ==================== DETALLE DE CLASE ====================

function verDetalleClase(claseId) {
    console.log("Ver detalle clase:", claseId);
    
    const clase = horariosGlobal.find(h => h.id === claseId);
    if (!clase) return;
    
    claseSeleccionadaGlobal = clase;
    const maestro = maestrosGlobal.find(m => m.id === clase.maestro_id);
    const icono = iconosPorTipo[clase.tipo_clase] || '🥋';
    const inscritos = clase.alumnos_inscritos || 0;
    const capacidad = clase.capacidad_maxima || 20;
    const porcentaje = Math.round((inscritos / capacidad) * 100);
    
    let colorBarra = '#e94560';
    if (porcentaje >= 90) colorBarra = '#ef4444';
    else if (porcentaje >= 70) colorBarra = '#f59e0b';
    else colorBarra = '#10b981';
    
    const modalBody = document.getElementById('modalBody');
    const modalTitulo = document.getElementById('modalTitulo');
    
    if (modalTitulo) {
        modalTitulo.innerHTML = `<i class="fas fa-info-circle"></i> ${clase.nombre}`;
    }
    
    if (modalBody) {
        modalBody.innerHTML = `
            <div style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <span style="font-size: 48px;">${icono}</span>
                    <span class="badge" style="background: ${clase.activo !== false ? '#10b981' : '#6b7280'}; color:white; padding:5px 12px; border-radius:20px;">
                        ${clase.activo !== false ? 'Activa' : 'Inactiva'}
                    </span>
                </div>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 15px; margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                        <span>📅 Día y hora</span>
                        <span><strong>${diasSemana[clase.dia_semana]} ${clase.hora_inicio} - ${clase.hora_fin}</strong></span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                        <span>👨‍🏫 Profesor</span>
                        <span><strong>${maestro ? `${maestro.nombre} ${maestro.apellidos}` : 'No asignado'}</strong></span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                        <span>🏷️ Tipo / Nivel</span>
                        <span><strong>${clase.tipo_clase} • ${clase.nivel}</strong></span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                        <span>📍 Salón</span>
                        <span><strong>${clase.salon || 'Principal'}</strong></span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>👥 Cupo</span>
                        <span><strong>${inscritos} / ${capacidad} (${porcentaje}%)</strong></span>
                    </div>
                </div>
                
                <div class="progress-bar" style="background: #eef2f6; border-radius: 10px; height: 10px; margin: 10px 0 20px 0;">
                    <div class="progress-fill" style="background: ${colorBarra}; width: ${porcentaje}%; height: 100%; border-radius: 10px;"></div>
                </div>
                
                <div class="modal-actions" style="display: flex; gap: 10px;">
                    <button class="btn-edit" onclick="editarClase()" style="flex:1; padding:12px; background:#3b82f6; color:white; border:none; border-radius:12px; cursor:pointer;">
                        <i class="fas fa-edit"></i> Editar
                    </button>
                    <button class="btn-attendance" onclick="tomarAsistenciaClase()" style="flex:1; padding:12px; background:#10b981; color:white; border:none; border-radius:12px; cursor:pointer;">
                        <i class="fas fa-check-circle"></i> Lista
                    </button>
                    <button class="btn-enroll" onclick="inscribirAlumnoClase()" style="flex:1; padding:12px; background:#e94560; color:white; border:none; border-radius:12px; cursor:pointer;">
                        <i class="fas fa-user-plus"></i> Inscribir
                    </button>
                </div>
            </div>
        `;
    }
    
    document.getElementById('modalClase').style.display = 'flex';
}

function cerrarModalClase() {
    document.getElementById('modalClase').style.display = 'none';
    claseSeleccionadaGlobal = null;
}

// Acciones del modal de clase
function tomarAsistenciaClase() {
    cerrarModalClase();
    if (claseSeleccionadaGlobal) {
        alert(`📋 Tomar asistencia para "${claseSeleccionadaGlobal.nombre}" - Funcionalidad en desarrollo`);
    }
}

function inscribirAlumnoClase() {
    if (!claseSeleccionadaGlobal) return;
    
    const alumnoId = prompt('Ingrese el ID del alumno a inscribir:');
    if (alumnoId && !isNaN(alumnoId)) {
        confirmarInscripcion(claseSeleccionadaGlobal.id, parseInt(alumnoId));
    } else if (alumnoId) {
        alert('Ingrese un ID válido (número)');
    }
    cerrarModalClase();
}

async function confirmarInscripcion(horarioId, alumnoId) {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`http://localhost:8000/api/v1/horarios/${horarioId}/inscribir?alumno_id=${alumnoId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ notas: '' })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error al inscribir');
        }
        
        alert('✅ Alumno inscrito correctamente');
        cargarHorarioSemanal();
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
}

// ==================== EDITAR CLASE ====================

function editarClase() {
    console.log("editarClase() llamada");
    
    if (!claseSeleccionadaGlobal) {
        console.error("No hay clase seleccionada");
        alert('No hay clase seleccionada');
        return;
    }
    
    console.log("Clase a editar:", claseSeleccionadaGlobal);
    cerrarModalClase();
    abrirModalEditarClase(claseSeleccionadaGlobal.id);
}

function abrirModalEditarClase(claseId) {
    console.log("abrirModalEditarClase llamada con ID:", claseId);
    
    const clase = horariosGlobal.find(h => h.id === claseId);
    if (!clase) {
        console.error("Clase no encontrada");
        alert('Clase no encontrada');
        return;
    }
    
    console.log("Datos de la clase:", clase);
    
    // Verificar que los elementos del formulario existen
    const editId = document.getElementById('edit_id');
    const editNombre = document.getElementById('edit_nombre');
    const editTipo = document.getElementById('edit_tipo');
    const editNivel = document.getElementById('edit_nivel');
    const editDia = document.getElementById('edit_dia');
    const editHoraInicio = document.getElementById('edit_hora_inicio');
    const editHoraFin = document.getElementById('edit_hora_fin');
    const editCapacidad = document.getElementById('edit_capacidad');
    const editSalon = document.getElementById('edit_salon');
    const editActivo = document.getElementById('edit_activo');
    const editMaestro = document.getElementById('edit_maestro');
    
    if (!editId || !editNombre) {
        console.error("No se encontraron los elementos del formulario de edición");
        alert('Error: Formulario de edición no encontrado');
        return;
    }
    
    // Llenar el formulario
    editId.value = clase.id;
    editNombre.value = clase.nombre;
    editTipo.value = clase.tipo_clase;
    editNivel.value = clase.nivel;
    editDia.value = clase.dia_semana;
    editHoraInicio.value = clase.hora_inicio;
    editHoraFin.value = clase.hora_fin;
    editCapacidad.value = clase.capacidad_maxima || 20;
    editSalon.value = clase.salon || 'Principal';
    editActivo.checked = clase.activo !== false;
    
    // Cargar maestros en el select
    if (editMaestro && maestrosGlobal && maestrosGlobal.length > 0) {
        console.log("Cargando maestros, cantidad:", maestrosGlobal.length);
        editMaestro.innerHTML = '<option value="">Seleccionar profesor</option>';
        maestrosGlobal.filter(m => m.activo).forEach(m => {
            const option = document.createElement('option');
            option.value = m.id;
            option.textContent = `${m.nombre} ${m.apellidos} - ${m.especialidad || 'General'}`;
            if (clase.maestro_id === m.id) option.selected = true;
            editMaestro.appendChild(option);
        });
    } else {
        console.warn("No hay maestros disponibles o select no encontrado");
        if (editMaestro) {
            editMaestro.innerHTML = '<option value="">No hay maestros registrados</option>';
        }
    }
    
    // Mostrar el modal
    const modal = document.getElementById('modalEditarHorario');
    if (modal) {
        console.log("Mostrando modal de edición");
        modal.style.display = 'flex';
    } else {
        console.error("Modal de edición no encontrado en el DOM");
        alert('Error: Modal de edición no encontrado');
    }
}

async function guardarEditarClase(event) {
    if (event) event.preventDefault();
    
    console.log("=== guardarEditarClase() INICIO ===");
    
    const id = document.getElementById('edit_id').value;
    if (!id) {
        alert('Error: No se encontró el ID de la clase');
        return;
    }
    
    console.log("ID de la clase a editar:", id);
    
    // Obtener valores del formulario
    const nombre = document.getElementById('edit_nombre').value;
    const tipo_clase = document.getElementById('edit_tipo').value;
    const nivel = document.getElementById('edit_nivel').value;
    const dia_semana = parseInt(document.getElementById('edit_dia').value);
    const hora_inicio = document.getElementById('edit_hora_inicio').value;
    const hora_fin = document.getElementById('edit_hora_fin').value;
    const capacidad_maxima = parseInt(document.getElementById('edit_capacidad').value);
    const salon = document.getElementById('edit_salon').value;
    const maestro_id = document.getElementById('edit_maestro').value || null;
    const activo = document.getElementById('edit_activo').checked;
    
    // Validaciones
    if (!nombre) {
        alert('❌ El nombre de la clase es requerido');
        return;
    }
    
    if (!hora_inicio || !hora_fin) {
        alert('❌ La hora de inicio y fin son requeridas');
        return;
    }
    
    if (hora_inicio >= hora_fin) {
        alert('❌ La hora de fin debe ser mayor a la hora de inicio');
        return;
    }
    
    // Construir objeto data
    const data = {
        nombre: nombre,
        tipo_clase: tipo_clase,
        nivel: nivel,
        dia_semana: dia_semana,
        hora_inicio: hora_inicio,
        hora_fin: hora_fin,
        capacidad_maxima: capacidad_maxima,
        salon: salon,
        maestro_id: maestro_id,
        activo: activo
    };
    
    console.log("Datos a enviar:", JSON.stringify(data, null, 2));
    
    try {
        const token = localStorage.getItem('access_token');
        if (!token) {
            alert('Sesión expirada. Por favor inicie sesión nuevamente');
            window.location.href = 'login.html';
            return;
        }
        
        const url = `http://localhost:8000/api/v1/horarios/${id}`;
        console.log("URL:", url);
        
        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        console.log("Response status:", response.status);
        
        // Leer la respuesta como texto primero para depuración
        const responseText = await response.text();
        console.log("Response text:", responseText);
        
        if (!response.ok) {
            let errorMessage = 'Error al actualizar';
            try {
                const errorJson = JSON.parse(responseText);
                errorMessage = errorJson.detail || errorJson.message || responseText;
            } catch(e) {
                errorMessage = responseText || `Error ${response.status}`;
            }
            throw new Error(errorMessage);
        }
        
        let result;
        try {
            result = JSON.parse(responseText);
        } catch(e) {
            result = responseText;
        }
        console.log("Respuesta del servidor:", result);
        
        alert('✅ Clase actualizada correctamente');
        cerrarModalEditarHorario();
        cargarHorarioSemanal(); // Recargar la tabla
        
    } catch (error) {
        console.error('Error detallado:', error);
        alert('❌ Error al actualizar clase: ' + error.message);
    }
}

function cerrarModalEditarHorario() {
    console.log("cerrarModalEditarHorario() llamada");
    const modal = document.getElementById('modalEditarHorario');
    if (modal) modal.style.display = 'none';
}

// ==================== NUEVA CLASE ====================

function abrirModalNuevoHorario() {
    console.log("abrirModalNuevoHorario() llamada");
    
    const form = document.getElementById('formNuevoHorario');
    if (form) form.reset();
    
    const capacidadInput = document.getElementById('new_capacidad');
    if (capacidadInput) capacidadInput.value = '20';
    
    const salonInput = document.getElementById('new_salon');
    if (salonInput) salonInput.value = 'Principal';
    
    const activoCheck = document.getElementById('new_activo');
    if (activoCheck) activoCheck.checked = true;
    
    const ahora = new Date();
    const horaSugerida = `${String(ahora.getHours() + 1).padStart(2, '0')}:00`;
    const horaInicio = document.getElementById('new_hora_inicio');
    if (horaInicio) horaInicio.value = horaSugerida;
    
    const horaFin = document.getElementById('new_hora_fin');
    if (horaFin) horaFin.value = `${String(ahora.getHours() + 2).padStart(2, '0')}:00`;
    
    cargarMaestrosEnSelect();
    
    const modal = document.getElementById('modalNuevoHorario');
    if (modal) modal.style.display = 'flex';
}

function cerrarModalNuevoHorario() {
    const modal = document.getElementById('modalNuevoHorario');
    if (modal) modal.style.display = 'none';
}

async function cargarMaestrosEnSelect() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('http://localhost:8000/api/v1/maestros/', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
            const maestros = await response.json();
            
            const selectNuevo = document.getElementById('new_maestro');
            if (selectNuevo) {
                selectNuevo.innerHTML = '<option value="">Seleccionar profesor</option>' +
                    maestros.filter(m => m.activo).map(m => 
                        `<option value="${m.id}">${m.nombre} ${m.apellidos} - ${m.especialidad || 'General'}</option>`
                    ).join('');
            }
        }
    } catch (error) {
        console.error('Error cargando maestros:', error);
    }
}

async function guardarNuevaClase(event) {
    event.preventDefault();
    console.log("guardarNuevaClase() llamada");
    
    const data = {
        nombre: document.getElementById('new_nombre').value,
        tipo_clase: document.getElementById('new_tipo').value,
        nivel: document.getElementById('new_nivel').value,
        dia_semana: parseInt(document.getElementById('new_dia').value),
        hora_inicio: document.getElementById('new_hora_inicio').value,
        hora_fin: document.getElementById('new_hora_fin').value,
        capacidad_maxima: parseInt(document.getElementById('new_capacidad').value),
        salon: document.getElementById('new_salon').value,
        maestro_id: document.getElementById('new_maestro').value || null,
        activo: document.getElementById('new_activo').checked
    };
    
    if (!data.nombre) {
        alert('❌ El nombre de la clase es requerido');
        return;
    }
    
    if (!data.hora_inicio || !data.hora_fin) {
        alert('❌ La hora de inicio y fin son requeridas');
        return;
    }
    
    if (data.hora_inicio >= data.hora_fin) {
        alert('❌ La hora de fin debe ser mayor a la hora de inicio');
        return;
    }
    
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('http://localhost:8000/api/v1/horarios/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error al crear');
        }
        
        alert('✅ Clase creada correctamente');
        cerrarModalNuevoHorario();
        cargarHorarioSemanal();
        
    } catch (error) {
        console.error('Error:', error);
        alert('❌ Error al crear clase: ' + error.message);
    }
}

// ==================== FUNCIONES DE PRUEBA Y DEPURACIÓN ====================

// Función para probar el modal directamente
function testModalEditar() {
    console.log("=== TEST: Abriendo modal directamente ===");
    const modal = document.getElementById('modalEditarHorario');
    if (modal) {
        modal.style.display = 'flex';
        console.log("Modal abierto");
    } else {
        console.error("Modal no encontrado");
        alert('Error: El modal de edición no existe en el DOM');
    }
}

// Función para verificar el estado de la clase seleccionada
function verEstadoClaseSeleccionada() {
    console.log("claseSeleccionadaGlobal:", claseSeleccionadaGlobal);
    if (claseSeleccionadaGlobal) {
        alert(`Clase seleccionada: ${claseSeleccionadaGlobal.nombre} (ID: ${claseSeleccionadaGlobal.id})`);
    } else {
        alert('No hay clase seleccionada. Haz clic en una clase primero.');
    }
}

// Versión alternativa de editarClase con más logs
function editarClaseAlternativa() {
    console.log("=== editarClaseAlternativa() ===");
    console.log("claseSeleccionadaGlobal:", claseSeleccionadaGlobal);
    
    if (!claseSeleccionadaGlobal) {
        console.error("No hay clase seleccionada");
        alert('Primero haz clic en una clase en la tabla');
        return;
    }
    
    console.log("Clase a editar:", claseSeleccionadaGlobal.nombre);
    
    // Cerrar modal de detalle
    const modalClase = document.getElementById('modalClase');
    if (modalClase) modalClase.style.display = 'none';
    
    // Abrir modal de edición
    const modalEditar = document.getElementById('modalEditarHorario');
    if (modalEditar) {
        // Llenar el formulario
        document.getElementById('edit_id').value = claseSeleccionadaGlobal.id;
        document.getElementById('edit_nombre').value = claseSeleccionadaGlobal.nombre;
        document.getElementById('edit_tipo').value = claseSeleccionadaGlobal.tipo_clase;
        document.getElementById('edit_nivel').value = claseSeleccionadaGlobal.nivel;
        document.getElementById('edit_dia').value = claseSeleccionadaGlobal.dia_semana;
        document.getElementById('edit_hora_inicio').value = claseSeleccionadaGlobal.hora_inicio;
        document.getElementById('edit_hora_fin').value = claseSeleccionadaGlobal.hora_fin;
        document.getElementById('edit_capacidad').value = claseSeleccionadaGlobal.capacidad_maxima || 20;
        document.getElementById('edit_salon').value = claseSeleccionadaGlobal.salon || 'Principal';
        document.getElementById('edit_activo').checked = claseSeleccionadaGlobal.activo !== false;
        
        // Cargar maestros en el select
        const select = document.getElementById('edit_maestro');
        if (select && maestrosGlobal) {
            select.innerHTML = '<option value="">Seleccionar profesor</option>';
            maestrosGlobal.forEach(m => {
                if (m.activo) {
                    const option = document.createElement('option');
                    option.value = m.id;
                    option.textContent = `${m.nombre} ${m.apellidos}`;
                    if (claseSeleccionadaGlobal.maestro_id === m.id) option.selected = true;
                    select.appendChild(option);
                }
            });
        }
        
        modalEditar.style.display = 'flex';
        console.log("Modal de edición abierto");
    } else {
        console.error("Modal de edición no encontrado");
        alert('Error: No se encontró el modal de edición');
    }
}

// Reemplazar la función editarClase original
window.editarClase = editarClaseAlternativa;
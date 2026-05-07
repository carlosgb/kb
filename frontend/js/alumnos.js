// frontend/js/alumnos.js
// Funciones específicas para la gestión de alumnos

let alumnosData = [];
let horariosDisponibles = [];
let alumnoSeleccionado = null;

// Cargar lista de alumnos
async function cargarAlumnos() {
    const search = document.getElementById('searchInput')?.value || '';
    const activo = document.getElementById('filtroActivo')?.value || '';
    const competidor = document.getElementById('filtroCompetidor')?.value || '';
    
    let params = [];
    if (search) params.push(`search=${encodeURIComponent(search)}`);
    if (activo) params.push(`activo=${activo}`);
    if (competidor) params.push(`es_competidor=${competidor}`);
    
    const query = params.length ? `?${params.join('&')}` : '';
    
    try {
        const alumnos = await getAlumnos(query);
        alumnosData = alumnos;
        
        // Cargar horarios para mostrar clases asignadas
        await cargarHorarios();
        
        // Para cada alumno, obtener sus clases inscritas
        for (const alumno of alumnos) {
            try {
                const inscripciones = await getInscripcionesAlumno(alumno.id);
                alumno.clases_asignadas = inscripciones || [];
            } catch (e) {
                alumno.clases_asignadas = [];
            }
        }
        
        renderTablaAlumnos(alumnos);
    } catch (error) {
        console.error('Error cargando alumnos:', error);
        const tbody = document.getElementById('alumnosTableBody');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; color: red;">Error cargando datos</td></tr>';
        }
    }
}

// Cargar horarios disponibles
async function cargarHorarios() {
    try {
        horariosDisponibles = await getHorarios();
        
        // Llenar selects de clases
        const selects = ['new_clase', 'edit_clase', 'asignarClaseId'];
        for (const selectId of selects) {
            const select = document.getElementById(selectId);
            if (select) {
                select.innerHTML = '<option value="">-- Seleccione una clase --</option>' +
                    horariosDisponibles.filter(h => h.activo).map(h => 
                        `<option value="${h.id}">${h.nombre} - ${h.dia_nombre} ${h.hora_inicio} (${h.tipo_clase})</option>`
                    ).join('');
            }
        }
    } catch (error) {
        console.error('Error cargando horarios:', error);
    }
}

// Renderizar tabla de alumnos
function renderTablaAlumnos(alumnos) {
    const tbody = document.getElementById('alumnosTableBody');
    
    if (!tbody) return;
    
    if (!alumnos || alumnos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align: center;">No hay alumnos registrados</td></tr>';
        return;
    }
    
    tbody.innerHTML = alumnos.map(alumno => {
        // Mostrar clases asignadas
        let clasesHtml = '';
        if (alumno.clases_asignadas && alumno.clases_asignadas.length > 0) {
            clasesHtml = alumno.clases_asignadas.map(c => {
                const horario = horariosDisponibles.find(h => h.id === c.horario_id);
                return `<div class="clase-asignada">
                            <span class="clase-nombre">${horario?.nombre || 'Clase'}</span>
                            <span class="clase-horario">${horario?.dia_nombre || ''} ${horario?.hora_inicio || ''}</span>
                        </div>`;
            }).join('');
        } else {
            clasesHtml = '<span class="text-muted">Sin clase asignada</span>';
        }
        
        return `
            <tr>
                <td>${alumno.id}</td>
                <td>
                    <strong>${alumno.nombre} ${alumno.apellidos}</strong><br>
                    <small class="text-muted">${alumno.grado_actual || 'Sin grado'}</small>
                </td>
                <td>${alumno.telefono_celular || 'N/A'}</td>
                <td>${alumno.email || 'N/A'}</td>
                <td>
                    ${clasesHtml}
                    <button class="btn-success" style="margin-top: 5px;" onclick="abrirModalAsignarClase(${alumno.id}, '${alumno.nombre} ${alumno.apellidos}')">
                        <i class="fas fa-plus"></i> Asignar Clase
                    </button>
                </td>
                <td>${alumno.grado_actual || 'Principiante'}</td>
                <td>
                    <span class="badge ${alumno.estado_pago === 'Al corriente' ? 'pagado' : 'vencido'}">
                        ${alumno.estado_pago || 'Al corriente'}
                    </span>
                </td>
                <td>
                    <span class="badge ${alumno.activo ? 'activo' : 'inactivo'}">
                        ${alumno.activo ? 'Activo' : 'Inactivo'}
                    </span>
                </td>
                <td class="acciones">
                    <button class="btn-icon" onclick="verDetalleAlumno(${alumno.id})" title="Ver detalles">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn-icon" onclick="editarAlumnoModal(${alumno.id})" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon" onclick="marcarAsistenciaAlumno(${alumno.id})" title="Marcar Asistencia">
                        <i class="fas fa-check-circle"></i>
                    </button>
                    <button class="btn-icon" onclick="registrarPagoAlumno(${alumno.id})" title="Registrar Pago">
                        <i class="fas fa-dollar-sign"></i>
                    </button>
                    <button class="btn-icon btn-danger" onclick="toggleActivoAlumno(${alumno.id}, ${!alumno.activo})" title="${alumno.activo ? 'Desactivar' : 'Activar'}">
                        <i class="fas ${alumno.activo ? 'fa-ban' : 'fa-check-circle'}"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// Obtener inscripciones del alumno
async function getInscripcionesAlumno(alumnoId) {
    try {
        return await apiCall(`/alumnos/${alumnoId}/inscripciones-clase`);
    } catch (error) {
        return [];
    }
}

// Abrir modal para asignar clase
function abrirModalAsignarClase(alumnoId, alumnoNombre) {
    alumnoSeleccionado = alumnoId;
    document.getElementById('asignarAlumnoNombre').value = alumnoNombre;
    document.getElementById('modalAsignarClase').style.display = 'flex';
}

// Confirmar asignación de clase
async function confirmarAsignarClase() {
    const claseId = document.getElementById('asignarClaseId').value;
    const notas = document.getElementById('asignarNotas').value;
    
    if (!claseId) {
        alert('Por favor seleccione una clase');
        return;
    }
    
    try {
        await inscribirClase(claseId, alumnoSeleccionado, { notas: notas });
        alert('✅ Clase asignada correctamente');
        cerrarModalAsignarClase();
        cargarAlumnos(); // Recargar lista
    } catch (error) {
        alert('❌ Error al asignar clase: ' + error.message);
    }
}

// Cerrar modal asignar clase
function cerrarModalAsignarClase() {
    document.getElementById('modalAsignarClase').style.display = 'none';
    alumnoSeleccionado = null;
    document.getElementById('asignarClaseId').value = '';
    document.getElementById('asignarNotas').value = '';
}

// Ver detalle del alumno
function verDetalleAlumno(id) {
    window.location.href = `alumno-detalle.html?id=${id}`;
}

// Marcar asistencia
async function marcarAsistenciaAlumno(id) {
    if (confirm('¿Marcar asistencia para este alumno?')) {
        try {
            await marcarAsistencia(id);
            alert('✅ Asistencia registrada correctamente');
            cargarAlumnos();
        } catch (error) {
            alert('❌ Error al registrar asistencia: ' + error.message);
        }
    }
}

// Registrar pago
async function registrarPagoAlumno(id) {
    if (confirm('¿Registrar pago de mensualidad?')) {
        try {
            await pagarMensualidad(id);
            alert('✅ Pago registrado correctamente');
            cargarAlumnos();
        } catch (error) {
            alert('❌ Error al registrar pago: ' + error.message);
        }
    }
}

// Activar/Desactivar alumno
async function toggleActivoAlumno(id, activo) {
    const accion = activo ? 'activar' : 'desactivar';
    if (confirm(`¿${activo ? 'Activar' : 'Desactivar'} este alumno?`)) {
        try {
            await updateAlumnoCompleto(id, { activo: activo });
            alert(`✅ Alumno ${accion}do correctamente`);
            cargarAlumnos();
        } catch (error) {
            alert(`❌ Error al ${accion} alumno: ` + error.message);
        }
    }
}

// Abrir modal para editar alumno
async function editarAlumnoModal(id) {
    try {
        const alumno = await getAlumno(id);
        const inscripciones = await getInscripcionesAlumno(id);
        const claseActual = inscripciones.length > 0 ? inscripciones[0].horario_id : '';
        
        document.getElementById('edit_id').value = alumno.id;
        document.getElementById('edit_nombre').value = alumno.nombre;
        document.getElementById('edit_apellidos').value = alumno.apellidos;
        document.getElementById('edit_sexo').value = alumno.sexo;
        document.getElementById('edit_fecha_nacimiento').value = alumno.fecha_nacimiento;
        document.getElementById('edit_telefono').value = alumno.telefono_celular || '';
        document.getElementById('edit_email').value = alumno.email || '';
        document.getElementById('edit_calle').value = alumno.calle || '';
        document.getElementById('edit_numero').value = alumno.numero || '';
        document.getElementById('edit_colonia').value = alumno.colonia || '';
        document.getElementById('edit_ciudad').value = alumno.ciudad || '';
        document.getElementById('edit_codigo_postal').value = alumno.codigo_postal || '';
        document.getElementById('edit_altura').value = alumno.altura;
        document.getElementById('edit_peso').value = alumno.peso_actual;
        document.getElementById('edit_grado').value = alumno.grado_actual;
        document.getElementById('edit_clase').value = claseActual;
        document.getElementById('edit_competidor').checked = alumno.es_competidor;
        document.getElementById('edit_activo').checked = alumno.activo;
        
        document.getElementById('modalEditarAlumno').style.display = 'flex';
    } catch (error) {
        alert('Error al cargar datos del alumno: ' + error.message);
    }
}

// Guardar edición de alumno
async function guardarEdicionAlumno() {
    const id = document.getElementById('edit_id').value;
    const nuevaClaseId = document.getElementById('edit_clase').value;
    
    const data = {
        nombre: document.getElementById('edit_nombre').value,
        apellidos: document.getElementById('edit_apellidos').value,
        sexo: document.getElementById('edit_sexo').value,
        fecha_nacimiento: document.getElementById('edit_fecha_nacimiento').value,
        telefono_celular: document.getElementById('edit_telefono').value,
        email: document.getElementById('edit_email').value || null,
        calle: document.getElementById('edit_calle').value,
        numero: document.getElementById('edit_numero').value || null,
        colonia: document.getElementById('edit_colonia').value || null,
        ciudad: document.getElementById('edit_ciudad').value,
        codigo_postal: document.getElementById('edit_codigo_postal').value || null,
        altura: parseFloat(document.getElementById('edit_altura').value),
        peso_actual: parseFloat(document.getElementById('edit_peso').value),
        grado_actual: document.getElementById('edit_grado').value,
        es_competidor: document.getElementById('edit_competidor').checked,
        activo: document.getElementById('edit_activo').checked
    };
    
    try {
        // Actualizar datos del alumno
        await updateAlumnoCompleto(id, data);
        
        // Si cambió la clase, actualizar inscripción
        const inscripcionesActuales = await getInscripcionesAlumno(id);
        const claseActualId = inscripcionesActuales.length > 0 ? inscripcionesActuales[0].horario_id : null;
        
        if (nuevaClaseId !== claseActualId) {
            // Dar de baja de clase anterior si existe
            if (claseActualId) {
                try {
                    await apiCall(`/alumnos/${id}/clases/${claseActualId}`, 'DELETE');
                } catch (e) {}
            }
            // Inscribir a nueva clase
            if (nuevaClaseId) {
                await inscribirClase(nuevaClaseId, id, {});
            }
        }
        
        alert('✅ Alumno actualizado correctamente');
        cerrarModalEditar();
        cargarAlumnos();
    } catch (error) {
        alert('❌ Error al actualizar alumno: ' + error.message);
    }
}

// Abrir modal para nuevo alumno
function abrirModalNuevoAlumno() {
    document.getElementById('formNuevoAlumno').reset();
    document.getElementById('new_ciudad').value = 'Ciudad de México';
    document.getElementById('new_grado').value = 'Principiante';
    document.getElementById('new_monto').value = '500';
    document.getElementById('modalNuevoAlumno').style.display = 'flex';
}

// Guardar nuevo alumno
async function guardarNuevoAlumno() {
    const claseId = document.getElementById('new_clase').value;
    
    const data = {
        nombre: document.getElementById('new_nombre').value,
        apellidos: document.getElementById('new_apellidos').value,
        sexo: document.getElementById('new_sexo').value,
        fecha_nacimiento: document.getElementById('new_fecha_nacimiento').value,
        telefono_celular: document.getElementById('new_telefono').value,
        email: document.getElementById('new_email').value || null,
        calle: document.getElementById('new_calle').value,
        numero: document.getElementById('new_numero').value || null,
        colonia: document.getElementById('new_colonia').value || null,
        ciudad: document.getElementById('new_ciudad').value,
        codigo_postal: document.getElementById('new_codigo_postal').value || null,
        altura: parseFloat(document.getElementById('new_altura').value),
        peso_actual: parseFloat(document.getElementById('new_peso').value),
        grado_actual: document.getElementById('new_grado').value,
        es_competidor: document.getElementById('new_competidor').checked,
        monto_mensualidad: parseFloat(document.getElementById('new_monto').value)
    };
    
    // Validaciones
    if (!data.nombre || !data.apellidos || !data.fecha_nacimiento || !data.telefono_celular || !data.calle || !data.altura || !data.peso_actual) {
        alert('Por favor complete todos los campos requeridos (*)');
        return;
    }
    
    try {
        const nuevoAlumno = await createAlumno(data);
        
        // Asignar clase si se seleccionó
        if (claseId) {
            await inscribirClase(claseId, nuevoAlumno.id, {});
        }
        
        alert('✅ Alumno registrado correctamente');
        cerrarModalNuevo();
        cargarAlumnos();
    } catch (error) {
        alert('❌ Error al registrar alumno: ' + error.message);
    }
}

// Cerrar modales
function cerrarModalEditar() {
    document.getElementById('modalEditarAlumno').style.display = 'none';
}

function cerrarModalNuevo() {
    document.getElementById('modalNuevoAlumno').style.display = 'none';
}

// Exportar a CSV
function exportarAlumnos() {
    if (!alumnosData || alumnosData.length === 0) {
        alert('No hay datos para exportar');
        return;
    }
    
    const headers = ['ID', 'Nombre', 'Apellidos', 'Sexo', 'Fecha Nacimiento', 'Teléfono', 'Email', 'Calle', 'Ciudad', 'Altura', 'Peso', 'Grado', 'Clase Asignada', 'Competidor', 'Estado', 'Asistencias'];
    const rows = alumnosData.map(a => [
        a.id,
        a.nombre,
        a.apellidos,
        a.sexo === 'M' ? 'Masculino' : (a.sexo === 'F' ? 'Femenino' : 'Otro'),
        a.fecha_nacimiento,
        a.telefono_celular || '',
        a.email || '',
        a.calle || '',
        a.ciudad || '',
        a.altura,
        a.peso_actual,
        a.grado_actual,
        a.clases_asignadas?.map(c => {
            const horario = horariosDisponibles.find(h => h.id === c.horario_id);
            return horario?.nombre || '';
        }).join(', ') || 'Sin clase',
        a.es_competidor ? 'Sí' : 'No',
        a.activo ? 'Activo' : 'Inactivo',
        a.asistencias_totales
    ]);
    
    const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob(["\uFEFF" + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.href = url;
    link.setAttribute('download', `alumnos_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Función para inscribir a una clase (desde api.js)
async function inscribirClase(horarioId, alumnoId, data = {}) {
    return await apiCall(`/horarios/${horarioId}/inscribir?alumno_id=${alumnoId}`, 'POST', data);
}

// Inicializar eventos
document.addEventListener('DOMContentLoaded', () => {
    cargarAlumnos();
    
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', () => cargarAlumnos());
    }
    
    const filtroActivo = document.getElementById('filtroActivo');
    if (filtroActivo) {
        filtroActivo.addEventListener('change', () => cargarAlumnos());
    }
    
    const filtroCompetidor = document.getElementById('filtroCompetidor');
    if (filtroCompetidor) {
        filtroCompetidor.addEventListener('change', () => cargarAlumnos());
    }
    
    const formNuevo = document.getElementById('formNuevoAlumno');
    if (formNuevo) {
        formNuevo.addEventListener('submit', (e) => {
            e.preventDefault();
            guardarNuevoAlumno();
        });
    }
    
    const formEditar = document.getElementById('formEditarAlumno');
    if (formEditar) {
        formEditar.addEventListener('submit', (e) => {
            e.preventDefault();
            guardarEdicionAlumno();
        });
    }
});
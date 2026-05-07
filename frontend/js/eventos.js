// frontend/js/eventos.js
// Funciones para la gestión de eventos y torneos

let eventosData = [];
let alumnosData = [];
let eventoSeleccionado = null;

// Cargar eventos
async function cargarEventos() {
    const search = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const tipo = document.getElementById('filtroTipo')?.value || '';
    const estado = document.getElementById('filtroEstado')?.value || '';
    
    try {
        const eventos = await getEventos();
        eventosData = eventos;
        
        let filtrados = eventos;
        
        if (search) {
            filtrados = filtrados.filter(e => 
                e.titulo.toLowerCase().includes(search) || 
                (e.lugar && e.lugar.toLowerCase().includes(search))
            );
        }
        
        if (tipo) {
            filtrados = filtrados.filter(e => e.tipo === tipo);
        }
        
        if (estado === 'proximo') {
            filtrados = filtrados.filter(e => new Date(e.fecha) >= new Date());
        } else if (estado === 'finalizado') {
            filtrados = filtrados.filter(e => new Date(e.fecha) < new Date());
        }
        
        renderEventos(filtrados);
    } catch (error) {
        console.error('Error cargando eventos:', error);
        document.getElementById('eventosGrid').innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-circle"></i><p>Error cargando eventos</p></div>';
    }
}

// Renderizar eventos
function renderEventos(eventos) {
    const container = document.getElementById('eventosGrid');
    const meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
    
    if (!eventos || eventos.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-calendar-alt"></i>
                <p>No hay eventos registrados</p>
                <button class="btn-primary" style="margin-top: 15px;" onclick="abrirModalNuevoEvento()">
                    <i class="fas fa-plus"></i> Crear Evento
                </button>
            </div>
        `;
        return;
    }
    
    container.innerHTML = eventos.map(evento => {
        const fecha = new Date(evento.fecha);
        const hoy = new Date();
        const esProximo = fecha >= hoy;
        const estadoClass = esProximo ? (evento.activo !== false ? 'proximo' : 'cerrado') : 'finalizado';
        let estadoTexto = '';
        if (evento.activo === false) {
            estadoTexto = 'Inactivo';
        } else if (esProximo) {
            estadoTexto = 'Próximo';
        } else {
            estadoTexto = 'Finalizado';
        }
        
        return `
            <div class="evento-card ${evento.activo === false ? 'inactivo' : ''}">
                <div class="evento-header">
                    <span class="evento-fecha">${fecha.getDate()} ${meses[fecha.getMonth()]} ${fecha.getFullYear()}</span>
                    <span class="evento-estado ${estadoClass}">${estadoTexto}</span>
                    <h3>${evento.titulo} ${evento.activo === false ? '(Inactivo)' : ''}</h3>
                    <p><i class="fas fa-clock"></i> ${evento.hora} hrs</p>
                </div>
                <div class="evento-body">
                    <div class="evento-info">
                        <div class="info-item">
                            <i class="fas fa-map-marker-alt"></i>
                            <span>${evento.lugar}</span>
                        </div>
                        <div class="info-item">
                            <i class="fas fa-tag"></i>
                            <span>${evento.tipo}</span>
                        </div>
                        <div class="info-item">
                            <i class="fas fa-users"></i>
                            <span>${evento.total_inscritos || 0} inscritos</span>
                        </div>
                    </div>
                    ${evento.descripcion ? `
                        <div class="evento-descripcion">
                            <i class="fas fa-info-circle"></i> ${evento.descripcion.substring(0, 120)}${evento.descripcion.length > 120 ? '...' : ''}
                        </div>
                    ` : ''}
                    <div class="evento-footer">
                        <div>
                            <div class="costo">
                                $${evento.costo_inscripcion}
                                ${evento.costo_acompañante > 0 ? `<small> + $${evento.costo_acompañante}/acompañante</small>` : ''}
                            </div>
                            ${evento.fecha_cierre_inscripcion ? `<div class="inscritos">📅 Cierre: ${evento.fecha_cierre_inscripcion}</div>` : ''}
                        </div>
                        <div class="evento-actions">
                            <button class="btn-ver" onclick="verInscritos(${evento.id}, '${evento.titulo}')" title="Ver inscritos">
                                <i class="fas fa-list"></i>
                            </button>
                            <button class="btn-editar" onclick="editarEvento(${evento.id})" title="Editar evento">
                                <i class="fas fa-edit"></i>
                            </button>
                            ${esProximo && evento.activo !== false ? `
                                <button class="btn-inscribir" onclick="abrirModalInscripcion(${evento.id}, '${evento.titulo}')" title="Inscribir alumno">
                                    <i class="fas fa-user-plus"></i>
                                </button>
                            ` : ''}
                            <button class="btn-eliminar" onclick="eliminarEvento(${evento.id})" title="${evento.activo !== false ? 'Desactivar evento' : 'Activar evento'}">
                                <i class="fas ${evento.activo !== false ? 'fa-ban' : 'fa-check-circle'}"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Cargar alumnos para inscripción
async function cargarAlumnosParaInscripcion() {
    try {
        alumnosData = await getAlumnos('?activo=true');
        const select = document.getElementById('inscribirAlumnoId');
        if (select) {
            select.innerHTML = '<option value="">-- Seleccione un alumno --</option>' +
                alumnosData.map(a => 
                    `<option value="${a.id}">${a.nombre} ${a.apellidos} - ${a.grado_actual || 'Principiante'}</option>`
                ).join('');
        }
    } catch (error) {
        console.error('Error cargando alumnos:', error);
    }
}

// Abrir modal nuevo evento
function abrirModalNuevoEvento() {
    document.getElementById('formNuevoEvento').reset();
    document.getElementById('new_fecha').value = new Date().toISOString().split('T')[0];
    document.getElementById('new_hora').value = '10:00';
    document.getElementById('new_costo_inscripcion').value = '0';
    document.getElementById('new_costo_acompanante').value = '0';
    document.getElementById('modalNuevoEvento').style.display = 'flex';
}

// Guardar nuevo evento
async function guardarNuevoEvento() {
    const data = {
        titulo: document.getElementById('new_titulo').value,
        fecha: document.getElementById('new_fecha').value,
        hora: document.getElementById('new_hora').value,
        lugar: document.getElementById('new_lugar').value,
        tipo: document.getElementById('new_tipo').value,
        costo_inscripcion: parseFloat(document.getElementById('new_costo_inscripcion').value) || 0,
        costo_acompañante: parseFloat(document.getElementById('new_costo_acompanante').value) || 0,
        fecha_cierre_inscripcion: document.getElementById('new_fecha_cierre').value || null,
        descripcion: document.getElementById('new_descripcion').value || null,
        activo: true
    };
    
    if (!data.titulo || !data.fecha || !data.hora || !data.lugar) {
        alert('Por favor complete todos los campos requeridos');
        return;
    }
    
    try {
        await createEvento(data);
        alert('✅ Evento creado correctamente');
        cerrarModalNuevoEvento();
        cargarEventos();
    } catch (error) {
        console.error('Error:', error);
        alert('❌ Error al crear evento: ' + (error.message || 'Error desconocido'));
    }
}

// Editar evento
async function editarEvento(eventoId) {
    try {
        const evento = await getEvento(eventoId);
        
        if (!evento) {
            alert('Evento no encontrado');
            return;
        }
        
        document.getElementById('edit_id').value = evento.id;
        document.getElementById('edit_titulo').value = evento.titulo;
        document.getElementById('edit_fecha').value = evento.fecha;
        document.getElementById('edit_hora').value = evento.hora;
        document.getElementById('edit_lugar').value = evento.lugar;
        document.getElementById('edit_tipo').value = evento.tipo;
        document.getElementById('edit_costo_inscripcion').value = evento.costo_inscripcion || 0;
        document.getElementById('edit_costo_acompanante').value = evento.costo_acompañante || 0;
        document.getElementById('edit_fecha_cierre').value = evento.fecha_cierre_inscripcion || '';
        document.getElementById('edit_descripcion').value = evento.descripcion || '';
        document.getElementById('edit_activo').checked = evento.activo !== false;
        
        document.getElementById('modalEditarEvento').style.display = 'flex';
    } catch (error) {
        console.error('Error cargando evento:', error);
        alert('❌ Error al cargar el evento: ' + (error.message || 'Error desconocido'));
    }
}

// Guardar edición de evento
async function guardarEditarEvento() {
    const id = document.getElementById('edit_id').value;
    
    const data = {
        titulo: document.getElementById('edit_titulo').value,
        fecha: document.getElementById('edit_fecha').value,
        hora: document.getElementById('edit_hora').value,
        lugar: document.getElementById('edit_lugar').value,
        tipo: document.getElementById('edit_tipo').value,
        costo_inscripcion: parseFloat(document.getElementById('edit_costo_inscripcion').value) || 0,
        costo_acompañante: parseFloat(document.getElementById('edit_costo_acompanante').value) || 0,
        fecha_cierre_inscripcion: document.getElementById('edit_fecha_cierre').value || null,
        descripcion: document.getElementById('edit_descripcion').value || null,
        activo: document.getElementById('edit_activo').checked
    };
    
    if (!data.titulo || !data.fecha || !data.hora || !data.lugar) {
        alert('Por favor complete todos los campos requeridos');
        return;
    }
    
    try {
        await updateEvento(id, data);
        alert('✅ Evento actualizado correctamente');
        cerrarModalEditarEvento();
        cargarEventos();
    } catch (error) {
        console.error('Error:', error);
        alert('❌ Error al actualizar evento: ' + (error.message || 'Error desconocido'));
    }
}

// Eliminar/Desactivar evento
async function eliminarEvento(eventoId) {
    const evento = eventosData.find(e => e.id === eventoId);
    if (!evento) return;
    
    const confirmMsg = evento.activo !== false 
        ? `¿Desactivar el evento "${evento.titulo}"? Los alumnos inscritos seguirán registrados.`
        : `¿Activar el evento "${evento.titulo}"?`;
    
    if (confirm(confirmMsg)) {
        try {
            await updateEvento(eventoId, { activo: !(evento.activo !== false) });
            alert(`✅ Evento ${evento.activo !== false ? 'desactivado' : 'activado'} correctamente`);
            cargarEventos();
        } catch (error) {
            console.error('Error:', error);
            alert('❌ Error al cambiar estado del evento: ' + (error.message || 'Error desconocido'));
        }
    }
}

// Abrir modal inscripción
function abrirModalInscripcion(eventoId, eventoNombre) {
    eventoSeleccionado = eventoId;
    document.getElementById('inscribirEventoNombre').value = eventoNombre;
    document.getElementById('inscribirAcompanantes').value = '0';
    document.getElementById('inscribirCategoria').value = '';
    document.getElementById('inscribirPeso').value = '';
    
    cargarAlumnosParaInscripcion();
    document.getElementById('modalInscripcion').style.display = 'flex';
}

// Confirmar inscripción
async function confirmarInscripcion() {
    const alumnoId = document.getElementById('inscribirAlumnoId').value;
    const acompanantes = parseInt(document.getElementById('inscribirAcompanantes').value) || 0;
    const categoria = document.getElementById('inscribirCategoria').value;
    const peso = document.getElementById('inscribirPeso').value;
    
    if (!alumnoId) {
        alert('Por favor seleccione un alumno');
        return;
    }
    
    const data = {
        num_acompañantes: acompanantes,
        categoria_inscrita: categoria || null,
        peso_registrado: peso ? parseFloat(peso) : null
    };
    
    try {
        await inscribirEvento(eventoSeleccionado, alumnoId, data);
        alert('✅ Alumno inscrito correctamente');
        cerrarModalInscripcion();
        cargarEventos();
    } catch (error) {
        console.error('Error:', error);
        alert('❌ Error al inscribir alumno: ' + (error.message || 'Error desconocido'));
    }
}

// Ver inscritos
async function verInscritos(eventoId, eventoNombre) {
    document.getElementById('verInscritosEventoNombre').value = eventoNombre;
    const container = document.getElementById('listaInscritos');
    container.innerHTML = '<div class="loading">Cargando inscritos...</div>';
    
    try {
        const inscritos = await getInscritosEvento(eventoId);
        
        if (!inscritos || inscritos.length === 0) {
            container.innerHTML = '<div class="empty-state"><p>No hay alumnos inscritos en este evento</p></div>';
        } else {
            container.innerHTML = inscritos.map(inscripcion => `
                <div class="inscrito-item">
                    <div class="inscrito-info">
                        <strong>${inscripcion.alumno_nombre || `Alumno ID: ${inscripcion.alumno_id}`}</strong>
                        <small>
                            Acompañantes: ${inscripcion.num_acompañantes || 0} | 
                            ${inscripcion.categoria_inscrita ? `Categoría: ${inscripcion.categoria_inscrita} | ` : ''}
                            ${inscripcion.peso_registrado ? `Peso: ${inscripcion.peso_registrado}kg` : ''}
                        </small>
                    </div>
                    <div>
                        <span class="inscrito-pago ${inscripcion.pagado ? 'pagado' : 'pendiente'}">
                            ${inscripcion.pagado ? 'Pagado' : 'Pendiente'}
                        </span>
                        ${!inscripcion.pagado ? `
                            <button class="btn-pago" onclick="confirmarPago(${inscripcion.id}, ${eventoId})">
                                Pagar
                            </button>
                        ` : ''}
                    </div>
                </div>
            `).join('');
        }
        
        document.getElementById('modalVerInscritos').style.display = 'flex';
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = '<div class="empty-state"><p>Error cargando inscritos</p></div>';
    }
}

// Confirmar pago
async function confirmarPago(inscripcionId, eventoId) {
    if (confirm('¿Confirmar pago de este alumno?')) {
        try {
            await confirmarPagoInscripcion(inscripcionId);
            alert('✅ Pago confirmado');
            verInscritos(eventoId, document.getElementById('verInscritosEventoNombre').value);
            cargarEventos();
        } catch (error) {
            console.error('Error:', error);
            alert('❌ Error al confirmar pago');
        }
    }
}

// Cerrar modales
function cerrarModalNuevoEvento() {
    document.getElementById('modalNuevoEvento').style.display = 'none';
}

function cerrarModalEditarEvento() {
    document.getElementById('modalEditarEvento').style.display = 'none';
}

function cerrarModalInscripcion() {
    document.getElementById('modalInscripcion').style.display = 'none';
    eventoSeleccionado = null;
}

function cerrarModalVerInscritos() {
    document.getElementById('modalVerInscritos').style.display = 'none';
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    cargarEventos();
    
    const formNuevo = document.getElementById('formNuevoEvento');
    if (formNuevo) {
        formNuevo.addEventListener('submit', (e) => {
            e.preventDefault();
            guardarNuevoEvento();
        });
    }
    
    const formEditar = document.getElementById('formEditarEvento');
    if (formEditar) {
        formEditar.addEventListener('submit', (e) => {
            e.preventDefault();
            guardarEditarEvento();
        });
    }
});
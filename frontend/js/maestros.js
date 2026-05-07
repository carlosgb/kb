// frontend/js/maestros.js
// Funciones para la gestión de maestros

let maestrosData = [];

// Cargar lista de maestros
async function cargarMaestros() {
    const search = document.getElementById('searchInput')?.value.toLowerCase() || '';
    
    try {
        const maestros = await getMaestros();
        maestrosData = maestros;
        
        let filtrados = maestros;
        if (search) {
            filtrados = maestros.filter(m => 
                m.nombre.toLowerCase().includes(search) || 
                m.apellidos.toLowerCase().includes(search) ||
                (m.especialidad && m.especialidad.toLowerCase().includes(search))
            );
        }
        
        renderMaestros(filtrados);
    } catch (error) {
        console.error('Error cargando maestros:', error);
        document.getElementById('maestrosGrid').innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-circle"></i><p>Error cargando maestros</p></div>';
    }
}

// Renderizar maestros
function renderMaestros(maestros) {
    const container = document.getElementById('maestrosGrid');
    
    if (!maestros || maestros.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-chalkboard-user"></i>
                <p>No hay maestros registrados</p>
                <button class="btn-primary" style="margin-top: 15px;" onclick="abrirModalNuevoMaestro()">
                    <i class="fas fa-plus"></i> Agregar Maestro
                </button>
            </div>
        `;
        return;
    }
    
    container.innerHTML = maestros.map(maestro => `
        <div class="maestro-card">
            <div class="maestro-header">
                <div class="maestro-avatar">
                    <i class="fas fa-user"></i>
                </div>
                <div class="maestro-info">
                    <h3>${maestro.nombre} ${maestro.apellidos}</h3>
                    <p>${maestro.especialidad || 'Sin especialidad'}</p>
                </div>
                <span class="badge ${maestro.activo ? 'activo' : 'inactivo'}">${maestro.activo ? 'Activo' : 'Inactivo'}</span>
            </div>
            <div class="maestro-details">
                <div class="detail-item">
                    <span><i class="fas fa-envelope"></i> Email</span>
                    <span>${maestro.email}</span>
                </div>
                <div class="detail-item">
                    <span><i class="fas fa-phone"></i> Teléfono</span>
                    <span>${maestro.telefono || 'No registrado'}</span>
                </div>
                <div class="detail-item">
                    <span><i class="fas fa-graduation-cap"></i> Grado</span>
                    <span>${maestro.grado || 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span><i class="fas fa-clock"></i> Años experiencia</span>
                    <span>${maestro.anos_experiencia} años</span>
                </div>
            </div>
            <div class="maestro-actions">
                <button class="btn-edit" onclick="editarMaestro(${maestro.id})">
                    <i class="fas fa-edit"></i> Editar
                </button>
                <button class="btn-horarios" onclick="verHorarios(${maestro.id})">
                    <i class="fas fa-calendar"></i> Horarios
                </button>
                <button class="btn-toggle ${maestro.activo ? 'btn-danger' : 'btn-success'}" onclick="toggleActivoMaestro(${maestro.id}, ${!maestro.activo})">
                    <i class="fas ${maestro.activo ? 'fa-ban' : 'fa-check-circle'}"></i>
                    ${maestro.activo ? 'Desactivar' : 'Activar'}
                </button>
            </div>
        </div>
    `).join('');
}

// Abrir modal nuevo maestro
function abrirModalNuevoMaestro() {
    document.getElementById('formNuevoMaestro').reset();
    document.getElementById('new_activo').checked = true;
    document.getElementById('modalNuevoMaestro').style.display = 'flex';
}

// Limpiar y validar teléfono
function limpiarTelefono(valor) {
    if (!valor) return null;
    let cleaned = valor.replace(/\D/g, '');
    if (cleaned.length >= 10) {
        return cleaned.substring(0, 15);
    } else if (cleaned.length > 0) {
        return null;
    }
    return null;
}

// Limpiar código postal
function limpiarCodigoPostal(valor) {
    if (!valor) return null;
    let cleaned = valor.replace(/\D/g, '');
    if (cleaned.length === 5) {
        return cleaned;
    }
    return null;
}

// Guardar nuevo maestro
async function guardarNuevoMaestro() {
    // Obtener y limpiar valores
    let nombre = document.getElementById('new_nombre').value.trim();
    let apellidos = document.getElementById('new_apellidos').value.trim();
    let sexo = document.getElementById('new_sexo').value;
    let fechaNacimiento = document.getElementById('new_fecha_nacimiento').value;
    let email = document.getElementById('new_email').value.trim();
    let telefonoRaw = document.getElementById('new_telefono').value;
    let telefonoEmergenciaRaw = document.getElementById('new_telefono_emergencia').value;
    let especialidad = document.getElementById('new_especialidad').value;
    let grado = document.getElementById('new_grado').value.trim();
    let anosExperiencia = parseInt(document.getElementById('new_anos_experiencia').value) || 0;
    let calle = document.getElementById('new_calle').value.trim();
    let numero = document.getElementById('new_numero').value.trim();
    let colonia = document.getElementById('new_colonia').value.trim();
    let ciudad = document.getElementById('new_ciudad').value.trim();
    let codigoPostalRaw = document.getElementById('new_codigo_postal').value;
    let activo = document.getElementById('new_activo').checked;
    
    // Validaciones básicas
    if (!nombre) {
        alert('El nombre es requerido');
        return;
    }
    if (!apellidos) {
        alert('Los apellidos son requeridos');
        return;
    }
    if (!email) {
        alert('El email es requerido');
        return;
    }
    if (!email.includes('@') || !email.includes('.')) {
        alert('Ingrese un email válido');
        return;
    }
    
    // Limpiar teléfonos
    let telefono = limpiarTelefono(telefonoRaw);
    let telefonoEmergencia = limpiarTelefono(telefonoEmergenciaRaw);
    let codigoPostal = limpiarCodigoPostal(codigoPostalRaw);
    
    // Validar teléfono requerido
    if (!telefono) {
        alert('Ingrese un número de teléfono válido (10-15 dígitos)');
        return;
    }
    
    // Validar sexo
    if (!['M', 'F', 'Otro'].includes(sexo)) {
        sexo = 'M';
    }
    
    // Validar fecha de nacimiento
    if (fechaNacimiento && fechaNacimiento > new Date().toISOString().split('T')[0]) {
        alert('La fecha de nacimiento no puede ser futura');
        return;
    }
    
    // Construir objeto de datos
    const data = {
        nombre: nombre,
        apellidos: apellidos,
        sexo: sexo,
        fecha_nacimiento: fechaNacimiento || null,
        email: email,
        telefono: telefono,
        telefono_emergencia: telefonoEmergencia,
        especialidad: especialidad,
        grado: grado || null,
        anos_experiencia: anosExperiencia,
        calle: calle || null,
        numero: numero || null,
        colonia: colonia || null,
        ciudad: ciudad || null,
        codigo_postal: codigoPostal,
        activo: activo
    };
    
    // Mostrar loading
    const btn = document.querySelector('#formNuevoMaestro button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Registrando...';
    btn.disabled = true;
    
    try {
        await createMaestro(data);
        alert('✅ Maestro registrado correctamente');
        cerrarModalNuevoMaestro();
        cargarMaestros();
    } catch (error) {
        console.error('Error:', error);
        alert('❌ Error al registrar maestro: ' + (error.message || 'Error desconocido'));
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Editar maestro
async function editarMaestro(maestroId) {
    try {
        const maestro = await getMaestro(maestroId);
        
        if (!maestro) {
            alert('Maestro no encontrado');
            return;
        }
        
        document.getElementById('edit_id').value = maestro.id;
        document.getElementById('edit_nombre').value = maestro.nombre;
        document.getElementById('edit_apellidos').value = maestro.apellidos;
        document.getElementById('edit_sexo').value = maestro.sexo || 'M';
        document.getElementById('edit_fecha_nacimiento').value = maestro.fecha_nacimiento || '';
        document.getElementById('edit_email').value = maestro.email;
        document.getElementById('edit_telefono').value = maestro.telefono || '';
        document.getElementById('edit_telefono_emergencia').value = maestro.telefono_emergencia || '';
        document.getElementById('edit_especialidad').value = maestro.especialidad || 'Kick Light';
        document.getElementById('edit_grado').value = maestro.grado || '';
        document.getElementById('edit_anos_experiencia').value = maestro.anos_experiencia || 0;
        document.getElementById('edit_calle').value = maestro.calle || '';
        document.getElementById('edit_numero').value = maestro.numero || '';
        document.getElementById('edit_colonia').value = maestro.colonia || '';
        document.getElementById('edit_ciudad').value = maestro.ciudad || '';
        document.getElementById('edit_codigo_postal').value = maestro.codigo_postal || '';
        document.getElementById('edit_activo').checked = maestro.activo;
        
        document.getElementById('modalEditarMaestro').style.display = 'flex';
    } catch (error) {
        console.error('Error cargando maestro:', error);
        alert('❌ Error al cargar datos del maestro: ' + (error.message || 'Error desconocido'));
    }
}

// Guardar edición de maestro
async function guardarEditarMaestro() {
    const id = document.getElementById('edit_id').value;
    
    // Obtener y limpiar valores
    let nombre = document.getElementById('edit_nombre').value.trim();
    let apellidos = document.getElementById('edit_apellidos').value.trim();
    let sexo = document.getElementById('edit_sexo').value;
    let fechaNacimiento = document.getElementById('edit_fecha_nacimiento').value;
    let email = document.getElementById('edit_email').value.trim();
    let telefonoRaw = document.getElementById('edit_telefono').value;
    let telefonoEmergenciaRaw = document.getElementById('edit_telefono_emergencia').value;
    let especialidad = document.getElementById('edit_especialidad').value;
    let grado = document.getElementById('edit_grado').value.trim();
    let anosExperiencia = parseInt(document.getElementById('edit_anos_experiencia').value) || 0;
    let calle = document.getElementById('edit_calle').value.trim();
    let numero = document.getElementById('edit_numero').value.trim();
    let colonia = document.getElementById('edit_colonia').value.trim();
    let ciudad = document.getElementById('edit_ciudad').value.trim();
    let codigoPostalRaw = document.getElementById('edit_codigo_postal').value;
    let activo = document.getElementById('edit_activo').checked;
    
    // Validaciones básicas
    if (!nombre) {
        alert('El nombre es requerido');
        return;
    }
    if (!apellidos) {
        alert('Los apellidos son requeridos');
        return;
    }
    if (!email) {
        alert('El email es requerido');
        return;
    }
    if (!email.includes('@') || !email.includes('.')) {
        alert('Ingrese un email válido');
        return;
    }
    
    // Limpiar teléfonos
    let telefono = limpiarTelefono(telefonoRaw);
    let telefonoEmergencia = limpiarTelefono(telefonoEmergenciaRaw);
    let codigoPostal = limpiarCodigoPostal(codigoPostalRaw);
    
    // Validar teléfono requerido
    if (!telefono) {
        alert('Ingrese un número de teléfono válido (10-15 dígitos)');
        return;
    }
    
    // Validar sexo
    if (!['M', 'F', 'Otro'].includes(sexo)) {
        sexo = 'M';
    }
    
    const data = {
        nombre: nombre,
        apellidos: apellidos,
        sexo: sexo,
        fecha_nacimiento: fechaNacimiento || null,
        email: email,
        telefono: telefono,
        telefono_emergencia: telefonoEmergencia,
        especialidad: especialidad,
        grado: grado || null,
        anos_experiencia: anosExperiencia,
        calle: calle || null,
        numero: numero || null,
        colonia: colonia || null,
        ciudad: ciudad || null,
        codigo_postal: codigoPostal,
        activo: activo
    };
    
    // Mostrar loading
    const btn = document.querySelector('#formEditarMaestro button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
    btn.disabled = true;
    
    try {
        await updateMaestro(id, data);
        alert('✅ Maestro actualizado correctamente');
        cerrarModalEditarMaestro();
        cargarMaestros();
    } catch (error) {
        console.error('Error:', error);
        alert('❌ Error al actualizar maestro: ' + (error.message || 'Error desconocido'));
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Activar/Desactivar maestro
async function toggleActivoMaestro(maestroId, activo) {
    const accion = activo ? 'activar' : 'desactivar';
    if (confirm(`¿${activo ? 'Activar' : 'Desactivar'} este maestro?`)) {
        try {
            await updateMaestro(maestroId, { activo: activo });
            alert(`✅ Maestro ${accion}do correctamente`);
            cargarMaestros();
        } catch (error) {
            console.error('Error:', error);
            alert(`❌ Error al ${accion} maestro`);
        }
    }
}

// Ver horarios del maestro
function verHorarios(maestroId) {
    window.location.href = `horarios.html?maestro_id=${maestroId}`;
}

// Cerrar modales
function cerrarModalNuevoMaestro() {
    document.getElementById('modalNuevoMaestro').style.display = 'none';
}

function cerrarModalEditarMaestro() {
    document.getElementById('modalEditarMaestro').style.display = 'none';
}

// Inicializar eventos
document.addEventListener('DOMContentLoaded', () => {
    cargarMaestros();
    
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', () => cargarMaestros());
    }
    
    const formNuevo = document.getElementById('formNuevoMaestro');
    if (formNuevo) {
        formNuevo.addEventListener('submit', (e) => {
            e.preventDefault();
            guardarNuevoMaestro();
        });
    }
    
    const formEditar = document.getElementById('formEditarMaestro');
    if (formEditar) {
        formEditar.addEventListener('submit', (e) => {
            e.preventDefault();
            guardarEditarMaestro();
        });
    }
    
    // Limpiar campos de teléfono automáticamente
    const limpiarInputTelefono = (input) => {
        if (input) {
            input.addEventListener('input', function() {
                this.value = this.value.replace(/[^0-9]/g, '').substring(0, 15);
            });
        }
    };
    
    const limpiarInputCP = (input) => {
        if (input) {
            input.addEventListener('input', function() {
                this.value = this.value.replace(/[^0-9]/g, '').substring(0, 5);
            });
        }
    };
    
    limpiarInputTelefono(document.getElementById('new_telefono'));
    limpiarInputTelefono(document.getElementById('new_telefono_emergencia'));
    limpiarInputTelefono(document.getElementById('edit_telefono'));
    limpiarInputTelefono(document.getElementById('edit_telefono_emergencia'));
    limpiarInputCP(document.getElementById('new_codigo_postal'));
    limpiarInputCP(document.getElementById('edit_codigo_postal'));
});
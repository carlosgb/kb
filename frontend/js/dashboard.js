// frontend/js/dashboard.js
let ingresosChart = null;

// Actualizar fecha y hora
function updateDateTime() {
    const now = new Date();
    const options = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    document.getElementById('dateTime').innerHTML = now.toLocaleDateString('es-MX', options);
}
setInterval(updateDateTime, 1000);
updateDateTime();

// Cargar dashboard completo
async function loadDashboard() {
    try {
        await Promise.all([
            loadStats(),
            loadAlertas(),
            loadProximosEventos(),
            loadTendencias(),
            loadTopAsistencia(),
            loadResumenFinanciero()
        ]);
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Cargar estadísticas principales
async function loadStats() {
    try {
        const stats = await getDashboardResumen();
        
        document.getElementById('totalAlumnos').innerText = stats.resumen?.alumnos_activos || 0;
        document.getElementById('totalMaestros').innerText = stats.resumen?.maestros_activos || 0;
        document.getElementById('clasesHoy').innerText = stats.resumen?.clases_hoy || 0;
        document.getElementById('eventosProximos').innerText = stats.resumen?.eventos_proximos || 0;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Cargar alertas
async function loadAlertas() {
    const container = document.getElementById('alertasList');
    try {
        const alertas = await getDashboardAlertas();
        
        if (!alertas.criticas && !alertas.advertencias) {
            container.innerHTML = '<div class="loading">✅ No hay alertas activas</div>';
            return;
        }
        
        let html = '';
        
        // Alertas críticas
        if (alertas.criticas) {
            if (alertas.criticas.pagos_vencidos > 0) {
                html += `
                    <div class="alerta-item critical">
                        <i class="fas fa-exclamation-circle"></i>
                        <div class="alerta-content">
                            <strong>Pagos Vencidos</strong>
                            <p>${alertas.criticas.pagos_vencidos} alumno(s) tienen pagos atrasados</p>
                        </div>
                        <span class="alerta-fecha">Urgente</span>
                    </div>
                `;
            }
            
            if (alertas.criticas.certificados_por_vencer > 0) {
                html += `
                    <div class="alerta-item critical">
                        <i class="fas fa-file-medical"></i>
                        <div class="alerta-content">
                            <strong>Certificados Médicos</strong>
                            <p>${alertas.criticas.certificados_por_vencer} certificados por vencer</p>
                        </div>
                        <span class="alerta-fecha">Próximo</span>
                    </div>
                `;
            }
        }
        
        // Advertencias
        if (alertas.advertencias) {
            if (alertas.advertencias.clases_sin_maestro > 0) {
                html += `
                    <div class="alerta-item warning">
                        <i class="fas fa-chalkboard-user"></i>
                        <div class="alerta-content">
                            <strong>Clases sin Maestro</strong>
                            <p>${alertas.advertencias.clases_sin_maestro} clase(s) no tienen profesor asignado</p>
                        </div>
                    </div>
                `;
            }
        }
        
        if (html === '') {
            html = '<div class="loading">✅ Todo en orden</div>';
        }
        
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = '<div class="loading">Error cargando alertas</div>';
        console.error(error);
    }
}

// Cargar próximos eventos
async function loadProximosEventos() {
    const container = document.getElementById('proximosEventos');
    try {
        const eventos = await getEventosProximos();
        
        if (!eventos || eventos.length === 0) {
            container.innerHTML = '<div class="loading">No hay eventos próximos</div>';
            return;
        }
        
        const meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
        
        let html = '';
        for (const evento of eventos.slice(0, 5)) {
            const fecha = new Date(evento.fecha);
            html += `
                <div class="evento-item">
                    <div class="evento-fecha">
                        <div class="dia">${fecha.getDate()}</div>
                        <div class="mes">${meses[fecha.getMonth()]}</div>
                    </div>
                    <div class="evento-info">
                        <strong>${evento.titulo}</strong>
                        <p><i class="fas fa-map-marker-alt"></i> ${evento.lugar}</p>
                        <p><i class="fas fa-clock"></i> ${evento.hora}</p>
                    </div>
                    <i class="fas fa-chevron-right" style="color: #ccc;"></i>
                </div>
            `;
        }
        
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = '<div class="loading">Error cargando eventos</div>';
        console.error(error);
    }
}

// Cargar tendencias de ingresos (gráfica)
async function loadTendencias() {
    const meses = document.getElementById('mesSelector')?.value || 6;
    try {
        const data = await getTendencias(meses);
        
        const labels = data.tendencias.map(t => t.mes);
        const ingresos = data.tendencias.map(t => t.pagos * 500); // Estimado
        
        const ctx = document.getElementById('ingresosChart').getContext('2d');
        
        if (ingresosChart) {
            ingresosChart.destroy();
        }
        
        ingresosChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Ingresos Estimados ($)',
                    data: ingresos,
                    borderColor: '#e94560',
                    backgroundColor: 'rgba(233, 69, 96, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#e94560',
                    pointBorderColor: 'white',
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `$${context.raw.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading trends:', error);
    }
}

// Cargar top de asistencia
async function loadTopAsistencia() {
    const container = document.getElementById('topAsistencia');
    try {
        const top = await getTopAsistencia();
        
        if (!top || top.length === 0) {
            container.innerHTML = '<div class="loading">No hay datos de asistencia</div>';
            return;
        }
        
        let html = '';
        for (let i = 0; i < Math.min(top.length, 5); i++) {
            const alumno = top[i];
            const topClass = i === 0 ? 'top-1' : (i === 1 ? 'top-2' : (i === 2 ? 'top-3' : ''));
            html += `
                <div class="ranking-item">
                    <div class="ranking-numero ${topClass}">${i + 1}</div>
                    <div class="ranking-info">
                        <strong>${alumno.nombre}</strong>
                        <p>${alumno.porcentaje_asistencia}% de asistencia</p>
                    </div>
                    <div class="ranking-valor">${alumno.total_asistencias} clases</div>
                </div>
            `;
        }
        
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = '<div class="loading">Error cargando ranking</div>';
        console.error(error);
    }
}

// Cargar resumen financiero
async function loadResumenFinanciero() {
    const container = document.getElementById('resumenFinanciero');
    try {
        const hoy = new Date();
        const mesActual = hoy.getMonth() + 1;
        const anioActual = hoy.getFullYear();
        
        const ingresos = await apiCall(`/reportes/financiero/ingresos-mensuales?anio=${anioActual}&mes=${mesActual}`);
        
        let html = `
            <div class="financeiro-item">
                <span>💰 Mensualidades</span>
                <strong>$${ingresos.detalle?.mensualidades?.toLocaleString() || 0}</strong>
            </div>
            <div class="financeiro-item">
                <span>🏆 Eventos</span>
                <strong>$${ingresos.detalle?.eventos?.toLocaleString() || 0}</strong>
            </div>
            <div class="financeiro-item">
                <span>🏥 Seguros</span>
                <strong>$${ingresos.detalle?.seguros?.toLocaleString() || 0}</strong>
            </div>
            <div class="financeiro-item">
                <span>🌍 Membresías WAKO</span>
                <strong>$${ingresos.detalle?.membresias_federativas?.toLocaleString() || 0}</strong>
            </div>
            <div class="financeiro-total">
                <span>Total del mes</span>
                <strong style="color: #e94560; font-size: 22px;">$${ingresos.total?.toLocaleString() || 0}</strong>
            </div>
        `;
        
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = '<div class="loading">Error cargando finanzas</div>';
        console.error(error);
    }
}

// Refresh manual
function refreshDashboard() {
    loadDashboard();
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
    setInterval(() => {
        loadStats();
        loadAlertas();
    }, 30000); // Actualizar cada 30 segundos
});
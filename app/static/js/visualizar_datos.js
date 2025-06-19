// Configuración global de Chart.js para mejorar el estilo
Chart.defaults.font.family = "'Inter', 'system-ui', 'sans-serif'";
Chart.defaults.font.size = 12;
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.padding = 20;

// Paleta de colores moderna
const colors = {
    primary: '#3B82F6',
    secondary: '#EF4444', 
    success: '#10B981',
    warning: '#F59E0B',
    purple: '#8B5CF6',
    pink: '#EC4899',
    teal: '#14B8A6',
    orange: '#F97316',
    gradient: {
        blue: ['#3B82F6', '#1D4ED8'],
        red: ['#EF4444', '#DC2626'],
        green: ['#10B981', '#059669'],
        purple: ['#8B5CF6', '#7C3AED']
    }
};

// Función para crear gradientes
function createGradient(ctx, color1, color2, vertical = false) {
    const gradient = vertical 
        ? ctx.createLinearGradient(0, 0, 0, 400)
        : ctx.createLinearGradient(0, 0, 400, 0);
    gradient.addColorStop(0, color1);
    gradient.addColorStop(1, color2);
    return gradient;
}

// Función principal para inicializar los gráficos
function initializeCharts() {
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            createDesercionDistribution(data);
            createEstadoAhorroActivo(data);
            createVariableImportance(data);
        })
        .catch(error => {
            console.error('Error al cargar los datos:', error);
            showError();
        });
}

// 1. Gráfico de Distribución de Deserción (Pie Chart mejorado)
function createDesercionDistribution(data) {
    const container = document.querySelector('.bg-gray-50.rounded-lg.p-8.text-center');
    if (!container) return;

    // Reemplazar el contenido placeholder
    container.innerHTML = `
        <div class="relative h-96">
            <canvas id="desercionChart" width="400" height="400"></canvas>
            <div class="mt-4 grid grid-cols-2 gap-4 text-sm">
                <div class="bg-white rounded-lg p-3 shadow-sm">
                    <div class="flex items-center justify-center mb-1">
                        <div class="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
                        <span class="font-medium">Fieles</span>
                    </div>
                    <div class="text-2xl font-bold text-blue-600" id="fielesCount">-</div>
                    <div class="text-gray-500" id="fielesPercent">-</div>
                </div>
                <div class="bg-white rounded-lg p-3 shadow-sm">
                    <div class="flex items-center justify-center mb-1">
                        <div class="w-3 h-3 bg-orange-500 rounded-full mr-2"></div>
                        <span class="font-medium">Desertores</span>
                    </div>
                    <div class="text-2xl font-bold text-orange-600" id="desertoresCount">-</div>
                    <div class="text-gray-500" id="desertoresPercent">-</div>
                </div>
            </div>
        </div>
    `;

    const ctx = document.getElementById('desercionChart').getContext('2d');
    const objCounts = data.obj_counts || data.target_counts || {};
    
    // Determinar las etiquetas y valores
    const labels = Object.keys(objCounts);
    const values = Object.values(objCounts);
    const total = values.reduce((a, b) => a + b, 0);

    // Actualizar estadísticas
    if (labels.length >= 2) {
        const fielesIndex = labels.findIndex(l => l.toLowerCase().includes('fiel') || l === '0');
        const desertoresIndex = labels.findIndex(l => l.toLowerCase().includes('desertor') || l === '1');
        
        if (fielesIndex !== -1) {
            document.getElementById('fielesCount').textContent = values[fielesIndex].toLocaleString();
            document.getElementById('fielesPercent').textContent = `${((values[fielesIndex] / total) * 100).toFixed(1)}%`;
        }
        
        if (desertoresIndex !== -1) {
            document.getElementById('desertoresCount').textContent = values[desertoresIndex].toLocaleString();
            document.getElementById('desertoresPercent').textContent = `${((values[desertoresIndex] / total) * 100).toFixed(1)}%`;
        }
    }

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels.map(label => 
                label.toLowerCase().includes('fiel') || label === '0' ? 'Clientes Fieles' : 
                label.toLowerCase().includes('desertor') || label === '1' ? 'Clientes Desertores' : label
            ),
            datasets: [{
                data: values,
                backgroundColor: [colors.primary, colors.orange],
                borderColor: ['#ffffff', '#ffffff'],
                borderWidth: 3,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 25,
                        font: {
                            size: 14,
                            weight: '500'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${context.parsed.toLocaleString()} (${percentage}%)`;
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                duration: 1500
            }
        }
    });
}

// 2. Gráfico de Estado Ahorro Activo (Bar Chart mejorado)
function createEstadoAhorroActivo(data) {
  const containers = document.querySelectorAll('.bg-gray-50.rounded-lg.p-8.text-center');
  const categoryContainer = containers[1]; // Segundo contenedor
  if (!categoryContainer) return;

  categoryContainer.innerHTML = `
    <div class="relative h-96">
      <canvas id="categoryChart"></canvas>
    </div>
  `;

  const ctx = document.getElementById('categoryChart').getContext('2d');

  // Sacamos los datos
  const counts = data.cat_counts?.estado_ahorro_activo || { '0': 0, '1': 0 };
  const labels = ['0', '1'];
  const values = [counts['0'] || 0, counts['1'] || 0];

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Clientes',
        data: values,
        backgroundColor: [ colors.primary, colors.orange ],
        borderRadius: 8,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          title: {
          display: true,
          text: 'estado_ahorro_activo',        // etiqueta para eje X
          font: {
            size: 14,
            weight: '500'
          },
          color: '#374151'
        },
          grid: { display: false },
          ticks: { font: { weight: '500', size: 14 } }
        },
        y: {
          title: {
          display: true,
          text: 'Cuentas',         // etiqueta para eje Y
          font: {
            size: 14,
            weight: '500'
          },
          color: '#374151'
        },
          beginAtZero: true,
          grid: { color: 'rgba(0,0,0,0.05)' },
          ticks: {
            callback: v => v.toLocaleString(),
            font: { size: 12 }
          }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: { /* tu configuración existente */ },
        datalabels: {
          anchor: 'end',
          align: 'end',
          font: { weight: '600', size: 12 },
          formatter: v => v.toLocaleString(),
          color: '#374151'  // un gris oscuro para contraste
        }
      },
      animation: {
        duration: 1500,
        easing: 'easeInOutQuart'
      }
    },
    plugins: [ ChartDataLabels ]  // habilita el plugin
  });
}


// 3. Gráfico de Variables que más Afectan la Deserción
function createVariableImportance(data) {
    // Buscar un contenedor después de las métricas o crear uno nuevo
    const metricsSection = document.querySelector('.grid.grid-cols-2.md\\:grid-cols-4.gap-6').parentElement;
    
    const importanceSection = document.createElement('div');
    importanceSection.className = 'bg-white rounded-xl shadow-sm border border-gray-200 p-6 mt-8';
    importanceSection.innerHTML = `
        <h2 class="text-xl font-semibold text-gray-900 mb-2">Variables con Mayor Impacto en Deserción</h2>
        <p class="text-gray-600 mb-6">Importancia de las características en el modelo predictivo (coeficientes absolutos)</p>
        <div class="relative h-96">
            <canvas id="importanceChart"></canvas>
        </div>
    `;
    
    metricsSection.parentElement.appendChild(importanceSection);

    const ctx = document.getElementById('importanceChart').getContext('2d');
    
    // Procesar datos de variable_importance
    let importanceArray = data.variable_importance || [];
    
    // Si no hay datos, mostrar error
    if (importanceArray.length === 0) {
        importanceSection.innerHTML = `
            <h2 class="text-xl font-semibold text-gray-900 mb-2">Variables con Mayor Impacto en Deserción</h2>
            <div class="text-center py-8">
                <p class="text-gray-500">No se encontraron datos de importancia de variables</p>
            </div>
        `;
        return;
    }

    // Ordenar por coeficiente absoluto (abs_coef) de mayor a menor
    const sortedData = importanceArray
        .sort((a, b) => b.abs_coef - a.abs_coef)
        .slice(0, 8); // Top 8 variables

    // Traducir nombres de variables a español
    const variableNames = {
        'calidad_servicio': 'Calidad del Servicio',
        'tasa_interes': 'Tasa de Interés',
        'estado_ahorro_activo': 'Estado Ahorro Activo',
        'n_productos_vigentes': 'N° Productos Vigentes',
        'edad': 'Edad',
        'porcentaje_pago': 'Porcentaje de Pago',
        'n_creditos_vigentes': 'N° Créditos Vigentes',
        'plazo_credito_meses': 'Plazo Crédito (meses)',
        'dias_de_mora': 'Días de Mora',
        'num_microseguros': 'N° Microseguros'
    };

    const labels = sortedData.map(item => 
        variableNames[item.variable] || item.variable
    );
    const values = sortedData.map(item => item.abs_coef);

    // Crear gradiente de colores basado en la importancia
    const backgroundColors = labels.map((_, i) => {
        const intensity = 0.8 - (i / labels.length) * 0.4;
        return `rgba(59, 130, 246, ${intensity})`;
    });

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Coeficiente Absoluto',
                data: values,
                backgroundColor: backgroundColors,
                borderColor: colors.primary,
                borderWidth: 1,
                borderRadius: 6,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(2);
                        },
                        font: {
                            size: 12
                        }
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 11,
                            weight: '500'
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const dataIndex = context.dataIndex;
                            const item = sortedData[dataIndex];
                            return [
                                `Coeficiente Absoluto: ${item.abs_coef.toFixed(3)}`,
                                `Coeficiente: ${item.coeficiente.toFixed(3)}`,
                                `Odds Ratio: ${item.odds_ratio.toFixed(3)}`
                            ];
                        }
                    }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeInOutQuart'
            }
        }
    });
}

// Función para mostrar error si no se pueden cargar los datos
function showError() {
    const containers = document.querySelectorAll('.bg-gray-50.rounded-lg.p-8.text-center');
    containers.forEach(container => {
        container.innerHTML = `
            <div class="text-center">
                <div class="bg-red-50 w-16 h-16 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                    </svg>
                </div>
                <p class="text-red-600 text-lg font-medium">Error al cargar los datos</p>
                <p class="text-gray-500 mt-2">Verifique que el archivo JSON esté disponible</p>
            </div>
        `;
    });
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Cargar Chart.js si no está disponible
    if (typeof Chart === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js';
        script.onload = initializeCharts;
        document.head.appendChild(script);
    } else {
        initializeCharts();
    }
});
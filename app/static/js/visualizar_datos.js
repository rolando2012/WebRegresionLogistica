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
            createMetrics(data);
            createROCCurve(data);
            createConfusionMatrix(data);
            createSigmoidFunction(data);
            
            // Cargar coeficientes por separado
            return fetch('/api/coeficientes');
        })
        .then(response => response.json())
        .then(coefData => {
            createCoeficientesChart(coefData);
        })
        .catch(error => {
            console.error('Error al cargar los datos:', error);
            showError();
        });
}
// 1. Gráfico de Distribución de Deserción (Pie Chart mejorado)
function createDesercionDistribution(data) {
    const container = document.querySelector('.bg-white.rounded-xl.shadow-sm.border.border-gray-200.p-6');
    if (!container) return;
    const targetArea = container.querySelector('.bg-gray-50.rounded-lg.p-8.text-center');
    if (!targetArea) return;

    // Reemplazar el contenido placeholder
    targetArea.innerHTML = `
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
    const labels = Object.keys(objCounts);
    const values = Object.values(objCounts);
    const total = values.reduce((a, b) => a + b, 0);

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
                legend: { position: 'bottom', labels: { padding: 25, font: { size: 14, weight: '500' } } },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${context.parsed.toLocaleString()} (${percentage}%)`;
                        }
                    }
                }
            },
            animation: { animateRotate: true, duration: 1500 }
        }
    });
}

// 2. Gráfico de Estado Ahorro Activo (Bar Chart mejorado)
function createEstadoAhorroActivo(data) {
    const containers = Array.from(document.querySelectorAll('.bg-white.rounded-xl.shadow-sm.border.border-gray-200.p-6'));
    if (containers.length < 2) return;
    const categoryContainer = containers[1].querySelector('.bg-gray-50.rounded-lg.p-8.text-center');
    if (!categoryContainer) return;

    categoryContainer.innerHTML = `
        <div class="relative h-96">
            <canvas id="categoryChart"></canvas>
        </div>
    `;

    const ctx = document.getElementById('categoryChart').getContext('2d');
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
                backgroundColor: [colors.primary, colors.orange], 
                borderRadius: 8, 
                borderSkipped: false 
            }] 
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { 
                    title: { display: true, text: 'estado_ahorro_activo', font: { size: 14, weight: '500' }, color: '#374151' }, 
                    grid: { display: false }, 
                    ticks: { font: { weight: '500', size: 14 } } 
                },
                y: { 
                    title: { display: true, text: 'Cuentas', font: { size: 14, weight: '500' }, color: '#374151' }, 
                    beginAtZero: true, 
                    grid: { color: 'rgba(0,0,0,0.05)' }, 
                    ticks: { callback: v => v.toLocaleString(), font: { size: 12 } } 
                }
            },
            plugins: { 
                legend: { display: false }, 
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Clientes: ${context.parsed.y.toLocaleString()}`;
                        }
                    }
                }
            },
            animation: { duration: 1500, easing: 'easeInOutQuart' }
        }
    });
}

// 3. Gráfico de Variables que más Afectan la Deserción
function createVariableImportance(data) {
    // Seleccionar contenedor principal de visualización
    const mainContainer = document.querySelector('.space-y-8');
    if (!mainContainer) return;

    const importanceSection = document.createElement('div');
    importanceSection.className = 'bg-white rounded-xl shadow-sm border border-gray-200 p-6 mt-8';
    importanceSection.innerHTML = `
        <h2 class="text-xl font-semibold text-gray-900 mb-2">Variables con Mayor Impacto en Deserción</h2>
        <p class="text-gray-600 mb-6">Importancia de las características en el modelo predictivo (coeficientes absolutos)</p>
        <div class="relative h-96">
            <canvas id="importanceChart"></canvas>
        </div>
    `;
    mainContainer.appendChild(importanceSection);

    const ctx = document.getElementById('importanceChart').getContext('2d');
    const importanceArray = data.variable_importance || [];
    if (importanceArray.length === 0) {
        importanceSection.innerHTML += `<div class="text-center py-8"><p class="text-gray-500">No se encontraron datos de importancia de variables</p></div>`;
        return;
    }

    const sortedData = importanceArray.sort((a, b) => b.abs_coef - a.abs_coef).slice(0, 8);
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
    const labels = sortedData.map(item => variableNames[item.variable] || item.variable);
    const values = sortedData.map(item => item.abs_coef);

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
                borderSkipped: false 
            }] 
        },
        options: {
            responsive: true, 
            maintainAspectRatio: false, 
            indexAxis: 'y',
            scales: { 
                x: { 
                    beginAtZero: true, 
                    grid: { color: 'rgba(0, 0, 0, 0.05)' }, 
                    ticks: { callback: v => v.toFixed(2), font: { size: 12 } } 
                }, 
                y: { 
                    grid: { display: false }, 
                    ticks: { font: { size: 11, weight: '500' } } 
                } 
            },
            plugins: { 
                legend: { display: false }, 
                tooltip: { 
                    callbacks: { 
                        label: function(context) { 
                            const item = sortedData[context.dataIndex]; 
                            return [
                                `Coeficiente Absoluto: ${item.abs_coef.toFixed(3)}`, 
                                `Coeficiente: ${item.coeficiente.toFixed(3)}`, 
                                `Odds Ratio: ${item.odds_ratio.toFixed(3)}`
                            ]; 
                        } 
                    } 
                } 
            },
            animation: { duration: 1500, easing: 'easeInOutQuart' }
        }
    });
}

// 4. Crear Métrica de Precisión
function createMetrics(data) {
  const metricsContainer = document.getElementById('metricsContainer');
  if (!metricsContainer) return;

  const metrics = data.metrics || {};
  const precision = (metrics.precision * 100).toFixed(1) || '0.0';

  metricsContainer.innerHTML = `
    <div class="max-w-xs bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200 mx-auto">
      <div class="flex items-center justify-between mb-4">
        <div class="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="text-right">
          <div class="text-4xl font-bold text-blue-600">${precision}%</div>
          <div class="text-sm text-blue-500 font-medium">Precisión</div>
        </div>
      </div>
      <!-- Barra de progreso -->
      <div class="w-full bg-gray-200 rounded-full h-2 mb-4">
        <div class="h-2 rounded-full" style="width: ${precision}%"></div>
      </div>
      <!-- Descripción ampliada -->
      <div class="text-sm text-gray-700 space-y-2">
        <p><strong>Fórmula:</strong> <code>Precisión = TP / (TP + FP)</code></p>
        <p>Este valor indica qué porcentaje de las veces que el modelo predijo "positivo", realmente fue positivo.</p>
        <p>Un valor alto sugiere pocas falsas alarmas (FP) y confianza en las predicciones positivas.</p>
      </div>
    </div>
  `;
}


// 5. Crear Curva ROC
function createROCCurve(data) {
    const ctx = document.getElementById('rocChart');
    if (!ctx) return;
    
    const context = ctx.getContext('2d');
    const rocData = data.rocData || data.roc || {};
    
    if (!rocData.fpr || !rocData.tpr) return;

    const fpr = rocData.fpr;
    const tpr = rocData.tpr;
    const auc = rocData.auc || 0;

    // Crear datos para la línea diagonal (clasificador aleatorio)
    const diagonalData = fpr.map(x => ({ x: x, y: x }));
    const rocPoints = fpr.map((x, i) => ({ x: x, y: tpr[i] }));

    new Chart(context, {
        type: 'line',
        data: {
            datasets: [{
                label: `ROC Curve (AUC = ${auc.toFixed(3)})`,
                data: rocPoints,
                borderColor: colors.primary,
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: false,
                borderWidth: 3,
                pointRadius: 0,
                pointHoverRadius: 6,
                tension: 0.1
            }, {
                label: 'Clasificador Aleatorio',
                data: diagonalData,
                borderColor: colors.orange,
                borderDash: [5, 5],
                fill: false,
                borderWidth: 2,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Tasa de Falsos Positivos',
                        font: { size: 14, weight: '500' },
                        color: '#374151'
                    },
                    min: 0,
                    max: 1,
                    grid: { color: 'rgba(0, 0, 0, 0.1)' },
                    ticks: { font: { size: 12 } }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Tasa de Verdaderos Positivos',
                        font: { size: 14, weight: '500' },
                        color: '#374151'
                    },
                    min: 0,
                    max: 1,
                    grid: { color: 'rgba(0, 0, 0, 0.1)' },
                    ticks: { font: { size: 12 } }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        font: { size: 12, weight: '500' }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: (${context.parsed.x.toFixed(3)}, ${context.parsed.y.toFixed(3)})`;
                        }
                    }
                }
            },
            animation: { duration: 1500, easing: 'easeInOutQuart' }
        }
    });
}

// 6. Crear Matriz de Confusión
function createConfusionMatrix(data) {
    const ctx = document.getElementById('confusionChart');
    if (!ctx) return;
    
    const context = ctx.getContext('2d');
    const cmData = data.cmData || {};
    const confusionMatrix = data.confusion_matrix || [];

    // Extraer valores de la matriz de confusión
    let TN, FP, FN, TP;
    
    if (cmData.TN !== undefined) {
        TN = cmData.TN;
        FP = cmData.FP;
        FN = cmData.FN;
        TP = cmData.TP;
    } else if (confusionMatrix.length === 2) {
        TN = confusionMatrix[0][0];
        FP = confusionMatrix[0][1];
        FN = confusionMatrix[1][0];
        TP = confusionMatrix[1][1];
    } else {
        return;
    }

    // Crear datos para el heatmap usando gráfico de barras apiladas
    const matrixData = [
        { x: 'Fiel', y: 'Fiel', v: TN, label: 'Verdadero Negativo' },
        { x: 'Fiel', y: 'Desertor', v: FN, label: 'Falso Negativo' },
        { x: 'Desertor', y: 'Fiel', v: FP, label: 'Falso Positivo' },
        { x: 'Desertor', y: 'Desertor', v: TP, label: 'Verdadero Positivo' }
    ];

    // Crear el gráfico como scatter plot personalizado
    new Chart(context, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Matriz de Confusión',
                data: matrixData.map((item, index) => ({
                    x: item.x === 'Fiel' ? 0 : 1,
                    y: item.y === 'Fiel' ? 0 : 1,
                    v: item.v,
                    label: item.label
                })),
                backgroundColor: function(context) {
                    const value = context.raw.v;
                    const maxValue = Math.max(TN, FP, FN, TP);
                    const intensity = value / maxValue;
                    if ((context.raw.x === 0 && context.raw.y === 0) || (context.raw.x === 1 && context.raw.y === 1)) {
                        return `rgba(34, 197, 94, ${0.3 + intensity * 0.7})`;
                    } else {
                        return `rgba(239, 68, 68, ${0.3 + intensity * 0.7})`;
                    }
                },
                borderColor: '#ffffff',
                borderWidth: 2,
                pointRadius: 50,
                pointHoverRadius: 55
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Predicción',
                        font: { size: 14, weight: '600' },
                        color: '#374151'
                    },
                    min: -0.5,
                    max: 1.5,
                    ticks: {
                        stepSize: 1,
                        callback: function(value) {
                            return value === 0 ? 'Fiel' : value === 1 ? 'Desertor' : '';
                        },
                        font: { size: 12, weight: '500' }
                    },
                    grid: { display: false }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Real',
                        font: { size: 14, weight: '600' },
                        color: '#374151'
                    },
                    min: -0.5,
                    max: 1.5,
                    ticks: {
                        stepSize: 1,
                        callback: function(value) {
                            return value === 0 ? 'Fiel' : value === 1 ? 'Desertor' : '';
                        },
                        font: { size: 12, weight: '500' }
                    },
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title: function() { return ''; },
                        label: function(context) {
                            const point = context.raw;
                            return [
                                point.label,
                                `Valor: ${point.v}`
                            ];
                        }
                    }
                }
            },
            animation: { duration: 1500, easing: 'easeInOutQuart' }
        },
        plugins: [{
            afterDatasetsDraw: function(chart) {
                const ctx = chart.ctx;
                chart.data.datasets.forEach((dataset, i) => {
                    const meta = chart.getDatasetMeta(i);
                    meta.data.forEach((element, index) => {
                        const data = dataset.data[index];
                        const position = element.getCenterPoint();
                        
                        ctx.fillStyle = '#ffffff';
                        ctx.font = 'bold 16px Inter';
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillText(data.v, position.x, position.y);
                    });
                });
            }
        }]
    });
}

// 7. Crear Función Sigmoide
function createSigmoidFunction(data) {
    const ctx = document.getElementById('sigmoidChart');
    if (!ctx) return;
    
    const context = ctx.getContext('2d');
    const sigmoidData = data.sigmoid || {};
    
    if (!sigmoidData.z || !sigmoidData.sigmoid) return;

    const sigmoidPoints = sigmoidData.z.map((z, i) => ({
        x: z,
        y: sigmoidData.sigmoid[i]
    }));

    new Chart(context, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Función Sigmoide',
                data: sigmoidPoints,
                borderColor: colors.purple,
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                fill: true,
                borderWidth: 3,
                pointRadius: 0,
                pointHoverRadius: 4,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'z (entrada del modelo)',
                        font: { size: 14, weight: '500' },
                        color: '#374151'
                    },
                    grid: { color: 'rgba(0, 0, 0, 0.1)' },
                    ticks: { font: { size: 12 } }
                },
                y: {
                    title: {
                        display: true,
                        text: 'σ(z) - Probabilidad',
                        font: { size: 14, weight: '500' },
                        color: '#374151'
                    },
                    min: 0,
                    max: 1,
                    grid: { color: 'rgba(0, 0, 0, 0.1)' },
                    ticks: { 
                        font: { size: 12 },
                        callback: function(value) {
                            return value.toFixed(1);
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        padding: 20,
                        font: { size: 12, weight: '500' }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `σ(${context.parsed.x.toFixed(2)}) = ${context.parsed.y.toFixed(4)}`;
                        }
                    }
                }
            },
            animation: { duration: 1500, easing: 'easeInOutQuart' }
        }
    });
}

// Función para crear el gráfico de coeficientes
function createCoeficientesChart(data) {
    const ctx = document.getElementById('coeficientesChart').getContext('2d');
    
    const labels = data.coeficientes.map(item => 
        item.variable.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    );
    const valores = data.coeficientes.map(item => item.coeficiente_beta);
    
    // Colores basados en si el coeficiente es positivo o negativo
    const backgroundColors = valores.map(val => 
        val >= 0 ? colors.success : colors.secondary
    );
    const borderColors = valores.map(val => 
        val >= 0 ? '#059669' : '#DC2626'
    );
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Coeficiente β',
                data: valores,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y', // Barras horizontales
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed.x;
                            const impact = value > 0 ? 'Aumenta deserción' : 'Reduce deserción';
                            return `β = ${value.toFixed(4)} (${impact})`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        color: '#E5E7EB'
                    },
                    title: {
                        display: true,
                        text: 'Coeficiente β',
                        font: {
                            weight: 'bold'
                        }
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                }
            }
        }
    });
    
    // Llenar la tabla
    fillCoeficientesTable(data);
}

// Función para llenar la tabla de coeficientes
function fillCoeficientesTable(data) {
    const tableBody = document.getElementById('coeficientesTable');
    
    const rows = data.coeficientes.map(item => {
        const variableFormatted = item.variable.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        const coeficiente = item.coeficiente_beta.toFixed(4);
        const impacto = item.coeficiente_beta >= 0 ? 'Aumenta deserción' : 'Reduce deserción';
        const impactoColor = item.coeficiente_beta >= 0 ? 'text-red-600' : 'text-green-600';
        
        return `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    ${variableFormatted}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono">
                    ${coeficiente}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm ${impactoColor} font-medium">
                    ${impacto}
                </td>
            </tr>
        `;
    }).join('');
    
    tableBody.innerHTML = rows;
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
    if (typeof Chart === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js';
        script.onload = initializeCharts;
        document.head.appendChild(script);
    } else {
        initializeCharts();
    }
});

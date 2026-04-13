/* ═══════════════════════════════════════════════════════════════════════
   Chart.js Visualizations
   ═══════════════════════════════════════════════════════════════════════ */

// Global chart defaults for dark theme
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(99, 102, 241, 0.1)';
Chart.defaults.font.family = "'Inter', sans-serif";

const chartInstances = {};

function destroyChart(id) {
    if (chartInstances[id]) {
        chartInstances[id].destroy();
        delete chartInstances[id];
    }
}

/* ── Gauge Chart (half doughnut) ─────────────────────────────────────── */
function renderGaugeChart(canvasId, score) {
    destroyChart(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const color = score >= 75 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444';
    const remaining = 100 - score;

    chartInstances[canvasId] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Score', 'Remaining'],
            datasets: [{
                data: [score, remaining],
                backgroundColor: [color, 'rgba(255,255,255,0.05)'],
                borderWidth: 0,
                circumference: 180,
                rotation: 270,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '75%',
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false },
            },
        },
        plugins: [{
            id: 'gaugeText',
            afterDraw(chart) {
                const { ctx, width, height } = chart;
                ctx.save();
                ctx.fillStyle = '#f1f5f9';
                ctx.font = "bold 36px 'JetBrains Mono', monospace";
                ctx.textAlign = 'center';
                ctx.fillText(`${Math.round(score)}`, width / 2, height * 0.65);
                ctx.font = "500 14px 'Inter', sans-serif";
                ctx.fillStyle = '#94a3b8';
                ctx.fillText('Overall Score', width / 2, height * 0.65 + 28);
                ctx.restore();
            },
        }],
    });
}

/* ── Radar Chart ─────────────────────────────────────────────────────── */
function renderRadarChart(canvasId, data) {
    destroyChart(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    chartInstances[canvasId] = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Readability', 'Efficiency', 'Maintainability', 'Optimization', 'Bug Safety', 'Complexity'],
            datasets: [{
                label: 'Code Metrics',
                data: [
                    data.readability || 0,
                    data.efficiency || 0,
                    data.maintainability || 0,
                    data.optimization || 0,
                    Math.max(0, 100 - (data.bugRisk || 0)),
                    data.complexityConfidence || 0,
                ],
                backgroundColor: 'rgba(99, 102, 241, 0.15)',
                borderColor: '#6366f1',
                borderWidth: 2,
                pointBackgroundColor: '#6366f1',
                pointBorderColor: '#fff',
                pointBorderWidth: 1,
                pointRadius: 4,
                pointHoverRadius: 6,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 25,
                        color: '#64748b',
                        backdropColor: 'transparent',
                        font: { size: 10 },
                    },
                    grid: { color: 'rgba(99, 102, 241, 0.08)' },
                    angleLines: { color: 'rgba(99, 102, 241, 0.1)' },
                    pointLabels: {
                        color: '#94a3b8',
                        font: { size: 11, weight: '500' },
                    },
                },
            },
            plugins: {
                legend: { display: false },
            },
        },
    });
}

/* ── Bar Chart ───────────────────────────────────────────────────────── */
function renderBarChart(canvasId, data) {
    destroyChart(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    chartInstances[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Quality', 'Readability', 'Efficiency', 'Maintainability', 'Optimization'],
            datasets: [{
                label: 'Score',
                data: [
                    data.quality || 0,
                    data.readability || 0,
                    data.efficiency || 0,
                    data.maintainability || 0,
                    data.optimization || 0,
                ],
                backgroundColor: [
                    'rgba(99, 102, 241, 0.7)',
                    'rgba(6, 182, 212, 0.7)',
                    'rgba(16, 185, 129, 0.7)',
                    'rgba(245, 158, 11, 0.7)',
                    'rgba(139, 92, 246, 0.7)',
                ],
                borderColor: [
                    '#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#8b5cf6',
                ],
                borderWidth: 1,
                borderRadius: 6,
                barPercentage: 0.6,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'x',
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(99, 102, 241, 0.06)' },
                    ticks: { font: { size: 11 } },
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 11, weight: '500' } },
                },
            },
            plugins: {
                legend: { display: false },
            },
        },
    });
}

/* ── Pie Chart ───────────────────────────────────────────────────────── */
function renderPieChart(canvasId, bugs) {
    destroyChart(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    // Group bugs by severity
    const severityCount = { critical: 0, high: 0, medium: 0, low: 0 };
    (bugs || []).forEach(bug => {
        severityCount[bug.severity || 'medium']++;
    });

    const hasBugs = Object.values(severityCount).some(c => c > 0);

    chartInstances[canvasId] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: hasBugs ? ['Critical', 'High', 'Medium', 'Low'] : ['No Bugs'],
            datasets: [{
                data: hasBugs
                    ? [severityCount.critical, severityCount.high, severityCount.medium, severityCount.low]
                    : [1],
                backgroundColor: hasBugs
                    ? ['#dc2626', '#ef4444', '#f59e0b', '#10b981']
                    : ['rgba(16, 185, 129, 0.3)'],
                borderWidth: 0,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '55%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        usePointStyle: true,
                        pointStyleWidth: 10,
                        font: { size: 11 },
                    },
                },
            },
        },
    });
}

/* ── Horizontal Bar Chart (Algorithm Confidence) ─────────────────────── */
function renderAlgoBarChart(canvasId, algorithms) {
    destroyChart(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const labels = (algorithms || []).map(a => a.name).slice(0, 6);
    const scores = (algorithms || []).map(a => a.confidence).slice(0, 6);

    if (labels.length === 0) {
        labels.push('No Algorithm Detected');
        scores.push(0);
    }

    const colors = [
        'rgba(99, 102, 241, 0.7)',
        'rgba(6, 182, 212, 0.7)',
        'rgba(16, 185, 129, 0.7)',
        'rgba(245, 158, 11, 0.7)',
        'rgba(139, 92, 246, 0.7)',
        'rgba(236, 72, 153, 0.7)',
    ];

    chartInstances[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Confidence %',
                data: scores,
                backgroundColor: colors.slice(0, labels.length),
                borderColor: colors.map(c => c.replace('0.7', '1')).slice(0, labels.length),
                borderWidth: 1,
                borderRadius: 6,
                barPercentage: 0.5,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(99, 102, 241, 0.06)' },
                    ticks: {
                        callback: v => v + '%',
                        font: { size: 11 },
                    },
                },
                y: {
                    grid: { display: false },
                    ticks: { font: { size: 11, weight: '500' } },
                },
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => `${ctx.parsed.x.toFixed(1)}% confidence`,
                    },
                },
            },
        },
    });
}

/* ── Render All Charts ───────────────────────────────────────────────── */
function renderAllCharts(analysisData) {
    // Gauge
    renderGaugeChart('chart-gauge', analysisData.code_quality_score || 0);

    // Radar
    renderRadarChart('chart-radar', {
        readability: analysisData.readability_score || 0,
        efficiency: analysisData.efficiency_score || 0,
        maintainability: analysisData.maintainability_score || 0,
        optimization: analysisData.optimization_score || 0,
        bugRisk: analysisData.bug_risk_level || 0,
        complexityConfidence: analysisData.complexity_confidence || 0,
    });

    // Bar
    renderBarChart('chart-bar', {
        quality: analysisData.code_quality_score || 0,
        readability: analysisData.readability_score || 0,
        efficiency: analysisData.efficiency_score || 0,
        maintainability: analysisData.maintainability_score || 0,
        optimization: analysisData.optimization_score || 0,
    });

    // Pie
    renderPieChart('chart-pie', analysisData.bugs || []);

    // Algorithm bar
    renderAlgoBarChart('chart-algo-bar', analysisData.all_algorithms || []);
}

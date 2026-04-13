/* ═══════════════════════════════════════════════════════════════════════
   Main Application Logic
   ═══════════════════════════════════════════════════════════════════════ */

let currentLanguage = 'python';
let lastAnalysisData = null;

// ── Tab Navigation ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    // Nav item clicks
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            switchTab(tab);
        });
    });

    // Language buttons
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentLanguage = btn.dataset.lang;
            updateLanguageSelectors(currentLanguage);
        });
    });

    // Upload zone
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');

    if (uploadZone && fileInput) {
        uploadZone.addEventListener('click', () => fileInput.click());
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });
        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) {
                handleFileSelect(e.dataTransfer.files[0]);
            }
        });
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });
    }
});

function switchTab(tabName) {
    // Update nav
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const activeNav = document.querySelector(`.nav-item[data-tab="${tabName}"]`);
    if (activeNav) activeNav.classList.add('active');

    // Update panels
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    const panel = document.getElementById(`panel-${tabName}`);
    if (panel) panel.classList.add('active');

    // Refresh editors
    setTimeout(() => {
        Object.values(editors).forEach(e => e.refresh());
    }, 100);
}

function updateLanguageSelectors(lang) {
    document.querySelectorAll('.select-input').forEach(sel => {
        sel.value = lang;
    });
    // Update editor modes
    Object.keys(editors).forEach(id => setEditorLanguage(id, lang));
}

// ── Utility Functions ───────────────────────────────────────────────────
function showLoading() {
    document.getElementById('loading-overlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.add('hidden');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function animateCounter(elementId, target, duration = 1200) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const start = 0;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(start + (target - start) * eased);
        el.textContent = current;
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

function animateRing(ringId, percentage) {
    const ring = document.getElementById(ringId);
    if (!ring) return;
    const circumference = 2 * Math.PI * 52; // r=52
    const dashArray = (percentage / 100) * circumference;
    ring.style.strokeDasharray = `${dashArray} ${circumference}`;
}

function animateProgressBar(barId, percentage) {
    const bar = document.getElementById(barId);
    if (bar) {
        setTimeout(() => { bar.style.width = `${percentage}%`; }, 100);
    }
}

// ── Generate Code ───────────────────────────────────────────────────────
async function handleGenerate() {
    const prompt = document.getElementById('generate-prompt').value.trim();
    const language = document.getElementById('generate-language').value;

    if (!prompt) {
        showToast('Please enter a description', 'error');
        return;
    }

    showLoading();
    try {
        const result = await api.generate(prompt, language);
        setEditorValue('generated-code-editor', result.generated_code);
        setEditorLanguage('generated-code-editor', result.language);

        // Show meta
        document.getElementById('generation-meta').classList.remove('hidden');
        document.getElementById('gen-model-type').textContent = `Model: ${result.model_type}`;
        document.getElementById('gen-tokens').textContent = `Tokens: ${result.tokens_generated}`;
        document.getElementById('gen-language').textContent = `Language: ${result.language}`;

        showToast('Code generated successfully!', 'success');
    } catch (err) {
        showToast('Generation failed: ' + err.message, 'error');
    } finally {
        hideLoading();
    }
}

function setPrompt(text) {
    document.getElementById('generate-prompt').value = text;
}

function copyGenerated() {
    const code = getEditorValue('generated-code-editor');
    navigator.clipboard.writeText(code).then(() => {
        showToast('Code copied to clipboard!', 'success');
    });
}

function downloadGenerated() {
    const code = getEditorValue('generated-code-editor');
    if (!code) return;
    const lang = document.getElementById('generate-language').value;
    const ext = { python: '.py', java: '.java', cpp: '.cpp' }[lang] || '.txt';
    downloadFile(`generated_code${ext}`, code);
}

function analyzeGenerated() {
    const code = getEditorValue('generated-code-editor');
    if (!code) { showToast('No generated code to analyze', 'error'); return; }
    setEditorValue('analyze-editor', code);
    switchTab('analyze');
    setTimeout(() => handleAnalyze(), 300);
}

// ── Analyze Code ────────────────────────────────────────────────────────
async function handleAnalyze() {
    const code = getEditorValue('analyze-editor');
    const language = document.getElementById('analyze-language').value;

    if (!code.trim()) {
        showToast('Please enter code to analyze', 'error');
        return;
    }

    showLoading();
    try {
        const data = await api.analyze(code, language);
        lastAnalysisData = data;
        renderAnalysisResults(data);
        showToast('Analysis complete!', 'success');
    } catch (err) {
        showToast('Analysis failed: ' + err.message, 'error');
    } finally {
        hideLoading();
    }
}

function renderAnalysisResults(data) {
    const results = document.getElementById('analysis-results');
    results.classList.remove('hidden');

    // Animate score rings
    animateCounter('score-quality', Math.round(data.code_quality_score));
    animateCounter('score-readability', Math.round(data.readability_score));
    animateCounter('score-efficiency', Math.round(data.efficiency_score));
    animateCounter('score-maintainability', Math.round(data.maintainability_score));

    animateRing('ring-quality', data.code_quality_score);
    animateRing('ring-readability', data.readability_score);
    animateRing('ring-efficiency', data.efficiency_score);
    animateRing('ring-maintainability', data.maintainability_score);

    // Metric cards
    document.getElementById('algorithm-name').textContent = data.algorithm_detected;
    document.getElementById('algorithm-confidence').textContent = `Confidence: ${data.algorithm_confidence}%`;
    document.getElementById('algorithm-detail').textContent = data.algorithm_details || '';
    animateProgressBar('bar-algorithm', data.algorithm_confidence);

    document.getElementById('complexity-value').textContent = data.time_complexity;
    document.getElementById('complexity-confidence').textContent = `Confidence: ${data.complexity_confidence}%`;
    document.getElementById('space-complexity').textContent = `Space: ${data.space_complexity}`;
    animateProgressBar('bar-complexity', data.complexity_confidence);

    document.getElementById('bug-risk-value').textContent = `${Math.round(data.bug_risk_level)}%`;
    document.getElementById('bugs-count').textContent = `Bugs Found: ${(data.bugs || []).length}`;
    animateProgressBar('bar-bugs', data.bug_risk_level);

    document.getElementById('optimization-value').textContent = `${Math.round(data.optimization_score)}%`;
    document.getElementById('optimization-count').textContent = `Suggestions: ${(data.optimization_suggestions || []).length}`;
    animateProgressBar('bar-optimization', data.optimization_score);

    // Render charts
    renderAllCharts(data);

    // Render detail lists
    renderBugsList(data.bugs || []);
    renderSuggestionsList(data.optimization_suggestions || []);
    renderPatternsList(data.patterns || []);

    // Scroll to results
    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderBugsList(bugs) {
    const container = document.getElementById('bugs-list');
    if (!bugs.length) {
        container.innerHTML = '<div class="empty-state">✅ No bugs detected — code looks clean!</div>';
        return;
    }
    container.innerHTML = bugs.map(bug => `
        <div class="bug-item severity-${bug.severity}">
            <div class="bug-type">${bug.type}</div>
            <div class="bug-desc">${bug.description}</div>
            <div class="bug-meta">
                ${bug.line ? `<span>Line ${bug.line}</span>` : ''}
                <span>Probability: ${bug.probability}%</span>
                <span>Severity: ${bug.severity}</span>
            </div>
        </div>
    `).join('');
}

function renderSuggestionsList(suggestions) {
    const container = document.getElementById('suggestions-list');
    if (!suggestions.length) {
        container.innerHTML = '<div class="empty-state">✅ Code is well-optimized!</div>';
        return;
    }
    container.innerHTML = suggestions.map(s => `
        <div class="suggestion-item">
            <div class="suggestion-desc">${s.description}</div>
            <div class="suggestion-meta">
                <span class="suggestion-category">${s.category}</span>
                <span class="suggestion-improvement">+${s.improvement_percentage}% improvement</span>
            </div>
        </div>
    `).join('');
}

function renderPatternsList(patterns) {
    const container = document.getElementById('patterns-list');
    if (!patterns.length) {
        container.innerHTML = '<div class="empty-state">No specific patterns detected</div>';
        return;
    }
    container.innerHTML = patterns.map(p => `
        <div class="pattern-item">
            <div class="pattern-name">${p.name}</div>
            <div class="pattern-desc">${p.description}</div>
            <div class="pattern-confidence">Confidence: ${p.confidence}%</div>
        </div>
    `).join('');
}

// ── Compare Code ────────────────────────────────────────────────────────
async function handleCompare() {
    const code1 = getEditorValue('compare-editor1');
    const code2 = getEditorValue('compare-editor2');
    const language = document.getElementById('compare-language').value;

    if (!code1.trim() || !code2.trim()) {
        showToast('Please enter code in both editors', 'error');
        return;
    }

    showLoading();
    try {
        const result = await api.similarity(code1, code2, language);
        renderCompareResults(result);
        showToast('Comparison complete!', 'success');
    } catch (err) {
        showToast('Comparison failed: ' + err.message, 'error');
    } finally {
        hideLoading();
    }
}

function renderCompareResults(data) {
    const results = document.getElementById('compare-results');
    results.classList.remove('hidden');

    document.getElementById('sim-overall').textContent = `${data.similarity_percentage.toFixed(1)}%`;
    document.getElementById('sim-token').textContent = `${data.token_similarity.toFixed(1)}%`;
    document.getElementById('sim-structure').textContent = `${data.structural_similarity.toFixed(1)}%`;

    animateProgressBar('bar-sim-overall', data.similarity_percentage);
    animateProgressBar('bar-sim-token', data.token_similarity);
    animateProgressBar('bar-sim-structure', data.structural_similarity);

    document.getElementById('sim-details-text').textContent = data.details;
}

// ── File Upload ─────────────────────────────────────────────────────────
let uploadedFile = null;

function handleFileSelect(file) {
    uploadedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
        const content = e.target.result;
        document.getElementById('upload-filename').textContent = file.name;
        setEditorValue('upload-code-editor', content);

        // Detect language from extension
        const ext = file.name.split('.').pop().toLowerCase();
        const langMap = { py: 'python', java: 'java', cpp: 'cpp', c: 'cpp', h: 'cpp' };
        const lang = langMap[ext] || 'python';
        setEditorLanguage('upload-code-editor', lang);

        document.getElementById('upload-preview').classList.remove('hidden');
    };
    reader.readAsText(file);
}

function clearUpload() {
    uploadedFile = null;
    document.getElementById('upload-preview').classList.add('hidden');
    document.getElementById('file-input').value = '';
}

async function handleUploadAnalyze() {
    if (!uploadedFile) {
        showToast('No file uploaded', 'error');
        return;
    }

    showLoading();
    try {
        const data = await api.upload(uploadedFile);
        lastAnalysisData = data;

        // Switch to analyze tab and show results
        switchTab('analyze');
        setEditorValue('analyze-editor', getEditorValue('upload-code-editor'));
        setTimeout(() => renderAnalysisResults(data), 200);

        showToast('File analyzed successfully!', 'success');
    } catch (err) {
        showToast('Upload analysis failed: ' + err.message, 'error');
    } finally {
        hideLoading();
    }
}

// ── Download ────────────────────────────────────────────────────────────
function downloadFile(filename, content) {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

function downloadReport() {
    if (!lastAnalysisData) {
        showToast('No analysis data to download', 'error');
        return;
    }

    const d = lastAnalysisData;
    const report = `
═══════════════════════════════════════════════════════════
  CodeIntel AI — Source Code Analysis Report
═══════════════════════════════════════════════════════════

Date: ${new Date().toLocaleString()}
Language: ${d.language}
Lines of Code: ${d.lines_of_code}
Functions: ${d.num_functions}
Classes: ${d.num_classes}

───────────────────────────────────────────────────────────
  QUALITY SCORES
───────────────────────────────────────────────────────────
Overall Code Quality:    ${d.code_quality_score}%
Readability Score:       ${d.readability_score}%
Efficiency Score:        ${d.efficiency_score}%
Maintainability Score:   ${d.maintainability_score}%
Optimization Score:      ${d.optimization_score}%

───────────────────────────────────────────────────────────
  ALGORITHM DETECTION
───────────────────────────────────────────────────────────
Detected Algorithm:      ${d.algorithm_detected}
Confidence:              ${d.algorithm_confidence}%
Details:                 ${d.algorithm_details || 'N/A'}

───────────────────────────────────────────────────────────
  COMPLEXITY ANALYSIS
───────────────────────────────────────────────────────────
Time Complexity:         ${d.time_complexity}
Space Complexity:        ${d.space_complexity}
Confidence:              ${d.complexity_confidence}%

───────────────────────────────────────────────────────────
  BUG DETECTION
───────────────────────────────────────────────────────────
Bug Risk Level:          ${d.bug_risk_level}%
Bugs Found:              ${(d.bugs || []).length}

${(d.bugs || []).map((b, i) => `  ${i+1}. [${b.severity.toUpperCase()}] ${b.type}
     ${b.description}
     Probability: ${b.probability}%${b.line ? ` (Line ${b.line})` : ''}`).join('\n\n')}

───────────────────────────────────────────────────────────
  OPTIMIZATION SUGGESTIONS
───────────────────────────────────────────────────────────
${(d.optimization_suggestions || []).map((s, i) => `  ${i+1}. [${s.category}] ${s.description}
     Potential improvement: +${s.improvement_percentage}%`).join('\n\n')}

───────────────────────────────────────────────────────────
  PATTERN RECOGNITION
───────────────────────────────────────────────────────────
${(d.patterns || []).map((p, i) => `  ${i+1}. ${p.name} (${p.confidence}% confidence)
     ${p.description}`).join('\n\n')}

═══════════════════════════════════════════════════════════
  Generated by CodeIntel AI — Deep Neural Network Analysis
═══════════════════════════════════════════════════════════
`.trim();

    downloadFile('code_analysis_report.txt', report);
    showToast('Report downloaded!', 'success');
}

// Research Evaluation & NLP Metrics Client JS

window.loadEvaluationView = async function() {
    try {
        const res = await fetch('/api/evaluation/metrics');
        const data = await res.json();
        if (data.success && data.results) {
            renderEvaluationMetrics(data.results);
        }
    } catch (e) {
        console.error("Error loading evaluation metrics:", e);
    }
};

window.loadRecommendationsView = async function() {
    try {
        const res = await fetch('/api/recommendations');
        const data = await res.json();
        if (data.success) {
            const container = document.getElementById('fullRecommendationsContainer');
            if (!container) return;

            let html = '';
            data.recommendations.forEach(r => {
                html += `
                    <div class="card" style="margin-bottom:1.25rem;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <span style="font-size:0.75rem;font-weight:700;color:var(--primary-cyan);">${r.category}</span>
                            <span style="font-size:0.75rem;color:var(--text-muted);">${r.duration}</span>
                        </div>
                        <h3 style="margin:0.5rem 0;">${r.title}</h3>
                        <p style="color:var(--text-muted);font-size:0.9rem;margin-bottom:0.75rem;">${r.description}</p>
                        <div style="font-size:0.8rem;color:var(--primary-indigo);">💡 <em>${r.reason}</em></div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }
    } catch (e) {
        console.error("Error loading recommendations:", e);
    }
};

function renderEvaluationMetrics(res) {
    // Intent Metrics
    const iAcc = document.getElementById('evalIntentAcc');
    const iF1 = document.getElementById('evalIntentF1');
    if (iAcc) iAcc.innerText = `${(res.intent_evaluation.accuracy * 100).toFixed(1)}%`;
    if (iF1) iF1.innerText = `${(res.intent_evaluation.macro_f1 * 100).toFixed(1)}%`;

    // Emotion Metrics
    const eAcc = document.getElementById('evalEmotionAcc');
    const eF1 = document.getElementById('evalEmotionF1');
    if (eAcc) eAcc.innerText = `${(res.emotion_evaluation.accuracy * 100).toFixed(1)}%`;
    if (eF1) eF1.innerText = `${(res.emotion_evaluation.macro_f1 * 100).toFixed(1)}%`;

    // Confusion Matrix for Emotion
    renderConfusionMatrixTable('emotionCMContainer', res.emotion_evaluation.labels, res.emotion_evaluation.confusion_matrix);
    
    // Confusion Matrix for Intent
    renderConfusionMatrixTable('intentCMContainer', res.intent_evaluation.labels, res.intent_evaluation.confusion_matrix);
}

function renderConfusionMatrixTable(containerId, labels, cm) {
    const container = document.getElementById(containerId);
    if (!container) return;

    let html = '<table class="metrics-table"><thead><tr><th style="text-align:left; background:rgba(30,41,59,0.85); min-width:90px;">Predicted →<br>Actual ↓</th>';
    labels.forEach(l => {
        html += `<th title="${l}">${l}</th>`;
    });
    html += '</tr></thead><tbody>';

    cm.forEach((row, rIdx) => {
        html += `<tr><td style="font-size:0.75rem; font-weight:700; text-align:left; background:rgba(30,41,59,0.5); color:var(--text-bright);">${labels[rIdx]}</td>`;
        row.forEach((val, cIdx) => {
            let cellClass = 'cm-zero';
            if (rIdx === cIdx) {
                cellClass = 'cm-diagonal';
            } else if (val > 0) {
                cellClass = 'cm-off-diagonal';
            }
            html += `<td class="${cellClass}">${val}</td>`;
        });
        html += '</tr>';
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

// Validated Mental Health Screening Questionnaires Client JS

let currentQuizType = 'PHQ-9';
const PHQ9_QUESTIONS = [
    "Little interest or pleasure in doing things?",
    "Feeling down, depressed, or hopeless?",
    "Trouble falling or staying asleep, or sleeping too much?",
    "Feeling tired or having little energy?",
    "Poor appetite or overeating?",
    "Feeling bad about yourself — or that you are a failure?",
    "Trouble concentrating on things, such as reading or watching TV?",
    "Moving or speaking so slowly that other people could have noticed?",
    "Thoughts that you would be better off dead, or of hurting yourself?"
];

const GAD7_QUESTIONS = [
    "Feeling nervous, anxious, or on edge?",
    "Not being able to stop or control worrying?",
    "Worrying too much about different things?",
    "Trouble relaxing?",
    "Being so restless that it is hard to sit still?",
    "Becoming easily annoyed or irritable?",
    "Feeling afraid as if something awful might happen?"
];

const OPTIONS = [
    { label: "Not at all", value: 0 },
    { label: "Several days", value: 1 },
    { label: "More than half the days", value: 2 },
    { label: "Nearly every day", value: 3 }
];

window.loadAssessmentsView = function() {
    renderQuestionnaireForm('PHQ-9');
    loadAssessmentHistory();
};

function renderQuestionnaireForm(type) {
    currentQuizType = type;
    const questions = type === 'PHQ-9' ? PHQ9_QUESTIONS : GAD7_QUESTIONS;
    const formContainer = document.getElementById('quizFormContainer');
    const titleEl = document.getElementById('quizTitle');

    if (titleEl) titleEl.innerText = `${type} Standardized Screening Questionnaire`;

    let html = '';
    questions.forEach((q, qIdx) => {
        html += `
            <div style="margin-bottom:1.25rem;padding:1rem;background:rgba(10,14,26,0.5);border:1px solid var(--border-color);border-radius:var(--radius-sm);">
                <div style="font-weight:600;font-size:0.95rem;margin-bottom:0.75rem;">${qIdx + 1}. ${q}</div>
                <div style="display:grid;grid-template-columns:repeat(4, 1fr);gap:0.5rem;">
        `;
        OPTIONS.forEach(opt => {
            html += `
                <label class="quiz-option">
                    <input type="radio" name="q_${qIdx}" value="${opt.value}" ${opt.value === 0 ? 'checked' : ''}>
                    <span style="font-size:0.85rem;">${opt.label}</span>
                </label>
            `;
        });
        html += `
                </div>
            </div>
        `;
    });

    html += `<button type="submit" class="btn-primary" style="margin-top:1rem;">Submit & Calculate ${type} Assessment</button>`;
    
    if (formContainer) {
        formContainer.innerHTML = html;
        const form = document.getElementById('assessmentQuizForm');
        form.onsubmit = submitQuestionnaire;
    }
}

async function submitQuestionnaire(e) {
    e.preventDefault();
    const questions = currentQuizType === 'PHQ-9' ? PHQ9_QUESTIONS : GAD7_QUESTIONS;
    const scores = [];

    for (let i = 0; i < questions.length; i++) {
        const selected = document.querySelector(`input[name="q_${i}"]:checked`);
        scores.push(selected ? parseInt(selected.value) : 0);
    }

    try {
        const res = await fetch('/api/assessments/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: currentQuizType, scores: scores })
        });
        const data = await res.json();
        if (data.success) {
            showToast(`${currentQuizType} Assessment Completed!`, 'success');
            renderAssessmentResultCard(data.result);
            loadAssessmentHistory();
            window.loadDashboardData();
        } else {
            showToast(data.message || 'Error submitting assessment', 'error');
        }
    } catch (err) {
        showToast('Server communication error submitting assessment', 'error');
    }
}

function renderAssessmentResultCard(result) {
    const card = document.getElementById('assessmentResultCard');
    if (!card) return;

    card.style.display = 'block';
    document.getElementById('assResultScore').innerText = `${result.score} / ${result.max_score} (${result.severity})`;
    document.getElementById('assResultInterpretation').innerText = result.interpretation;
    document.getElementById('assResultDisclaimer').innerText = result.disclaimer;
}

async function loadAssessmentHistory() {
    try {
        const res = await fetch('/api/assessments/history');
        const data = await res.json();
        if (data.success) {
            const tableBody = document.getElementById('assessmentHistoryTableBody');
            if (!tableBody) return;

            if (!data.assessments || data.assessments.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--text-muted);">No assessments recorded yet.</td></tr>';
                return;
            }

            let html = '';
            data.assessments.forEach(a => {
                html += `
                    <tr>
                        <td><strong>${a.assessment_type}</strong></td>
                        <td>${a.score} pts</td>
                        <td><span style="font-size:0.85rem;">${a.interpretation}</span></td>
                        <td>${new Date(a.date).toLocaleDateString()}</td>
                    </tr>
                `;
            });
            tableBody.innerHTML = html;
        }
    } catch (e) {
        console.error("Error loading assessment history:", e);
    }
}

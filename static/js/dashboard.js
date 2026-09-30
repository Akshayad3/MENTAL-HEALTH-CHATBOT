// Main Dashboard View Controller Client JS

window.loadDashboardData = async function() {
    try {
        const res = await fetch('/api/dashboard');
        const data = await res.json();
        if (data.success) {
            renderWellbeingOverview(data.wellbeing);
            renderRecentActivity(data.recent_activity);
            renderDashboardRecommendations(data.recommendations);
        }
    } catch (e) {
        console.error("Error loading dashboard data:", e);
    }
};

function renderWellbeingOverview(wb) {
    const statusBadge = document.getElementById('dashOverallStatus');
    const stressFill = document.getElementById('dashStressFill');
    const anxietyFill = document.getElementById('dashAnxietyFill');
    const sadnessFill = document.getElementById('dashSadnessFill');

    const stressVal = document.getElementById('dashStressVal');
    const anxietyVal = document.getElementById('dashAnxietyVal');
    const sadnessVal = document.getElementById('dashSadnessVal');

    const stressTrend = document.getElementById('dashStressTrend');
    const anxietyTrend = document.getElementById('dashAnxietyTrend');
    const moodTrend = document.getElementById('dashMoodTrend');

    if (statusBadge) {
        statusBadge.innerText = wb.overall_status;
        statusBadge.className = `status-badge ${wb.status_code === 'STABLE' ? 'status-stable' : wb.status_code === 'NEEDS_ATTENTION' ? 'status-warning' : 'status-danger'}`;
    }

    if (stressFill) stressFill.style.width = `${wb.indicators.stress}%`;
    if (anxietyFill) anxietyFill.style.width = `${wb.indicators.anxiety}%`;
    if (sadnessFill) sadnessFill.style.width = `${wb.indicators.sadness}%`;

    if (stressVal) stressVal.innerText = `${wb.raw_scores.stress}/10`;
    if (anxietyVal) anxietyVal.innerText = `${wb.raw_scores.anxiety}/10`;
    if (sadnessVal) sadnessVal.innerText = `${wb.raw_scores.sadness}/10`;

    if (stressTrend) stressTrend.innerText = wb.trends.stress;
    if (anxietyTrend) anxietyTrend.innerText = wb.trends.anxiety;
    if (moodTrend) moodTrend.innerText = wb.trends.mood;
}

function renderRecentActivity(activity) {
    const list = document.getElementById('dashRecentActivityList');
    if (!list) return;

    if (!activity || activity.length === 0) {
        list.innerHTML = '<p style="color:var(--text-muted);font-size:0.9rem;">No recent activities logged yet. Start a chat or take an assessment above!</p>';
        return;
    }

    let html = '';
    activity.forEach(act => {
        html += `
            <div style="display:flex;align-items:center;justify-content:space-between;padding:0.75rem;border-bottom:1px solid var(--border-color);">
                <div>
                    <strong style="font-size:0.9rem;">${act.title}</strong>
                    <div style="font-size:0.75rem;color:var(--text-subtle);">${act.subtitle}</div>
                </div>
                <span style="font-size:0.75rem;color:var(--text-muted);">${act.date}</span>
            </div>
        `;
    });
    list.innerHTML = html;
}

function renderDashboardRecommendations(recs) {
    const container = document.getElementById('dashRecommendationsList');
    if (!container) return;

    if (!recs || recs.length === 0) {
        container.innerHTML = '<p style="color:var(--text-muted);">Explore wellness exercises in the Recommendations tab.</p>';
        return;
    }

    let html = '';
    recs.slice(0, 3).forEach(r => {
        html += `
            <div class="card" style="padding:1rem;margin-bottom:0.75rem;">
                <div style="font-size:0.75rem;color:var(--primary-cyan);font-weight:600;">${r.category}</div>
                <h4 style="margin:0.25rem 0;font-size:1rem;">${r.title || r.recommendation}</h4>
                <p style="font-size:0.825rem;color:var(--text-muted);">${r.reason}</p>
            </div>
        `;
    });
    container.innerHTML = html;
}

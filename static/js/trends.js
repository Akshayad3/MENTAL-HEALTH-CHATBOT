// Mental Health Longitudinal Trends Analytics Client JS

let trendsChartInstance = null;

window.loadTrendsView = async function() {
    try {
        const res = await fetch('/api/trends/history');
        const data = await res.json();
        if (data.success && data.trends) {
            renderTrendsChart(data.trends);
        }
    } catch (e) {
        console.error("Error loading trends view:", e);
    }
};

function renderTrendsChart(trendsData) {
    const canvas = document.getElementById('longitudinalTrendsChart');
    if (!canvas) return;

    const labels = trendsData.map(t => t.date);
    const stressData = trendsData.map(t => t.stress_indicator);
    const anxietyData = trendsData.map(t => t.anxiety_indicator);
    const moodData = trendsData.map(t => t.mood_indicator);

    if (trendsChartInstance) {
        trendsChartInstance.destroy();
    }

    const ctx = canvas.getContext('2d');
    trendsChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Stress Indicator (0-10)',
                    data: stressData,
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    tension: 0.3,
                    fill: true
                },
                {
                    label: 'Anxiety Indicator (0-10)',
                    data: anxietyData,
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.1)',
                    tension: 0.3,
                    fill: true
                },
                {
                    label: 'Mood Index (0-10)',
                    data: moodData,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.3,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    min: 0,
                    max: 10,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                }
            },
            plugins: {
                legend: { labels: { color: '#f1f5f9' } }
            }
        }
    });
}

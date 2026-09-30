// Groundwork — Daily Habit Log Client JS

let currentHabitMonth = '2026-09';
let activeGwSubTab = 'tracker';
let selectedCalDate = '2026-09-24';
let analysisFilterType = 'month';
let currentHabitData = null;

const EMOJI_LIST = ['🏋️', '😴', '📖', '💧', '🚶', '🥗', '🧘', '🏃', '🍎', '💻', '📚', '🚴', '🧘‍♀️', '📌', '🎯', '✨'];
let selectedEmojiIndex = 0;

window.loadHabitsView = function() {
    switchGwSubTab(activeGwSubTab);
};

function switchGwSubTab(tab) {
    activeGwSubTab = tab;
    
    // Highlight active pill button
    const pills = document.querySelectorAll('.gw-pill-btn');
    pills.forEach(p => p.classList.remove('active'));
    
    const activePill = document.querySelector(`.gw-pill-btn[data-gw-tab="${tab}"]`);
    if (activePill) activePill.classList.add('active');
    
    // Hide all sub-views
    document.getElementById('gw-subview-tracker').style.display = 'none';
    document.getElementById('gw-subview-calendar').style.display = 'none';
    document.getElementById('gw-subview-analysis').style.display = 'none';
    
    // Show active sub-view
    document.getElementById(`gw-subview-${tab}`).style.display = 'block';
    
    if (tab === 'tracker') fetchAndRenderTracker();
    if (tab === 'calendar') fetchAndRenderCalendar();
    if (tab === 'analysis') fetchAndRenderAnalysis();
}

async function fetchAndRenderTracker() {
    try {
        const res = await fetch(`/api/habits?month=${currentHabitMonth}`);
        const result = await res.json();
        if (result.success) {
            currentHabitData = result.data;
            renderTrackerTable(result.data);
            updateDoneTodayBadge(result.data);
        }
    } catch (e) {
        console.error("Error loading habits data:", e);
    }
}

function renderTrackerTable(data) {
    const monthTitle = document.getElementById('gwMonthTitle');
    if (monthTitle) {
        const [y, m] = currentHabitMonth.split('-');
        const dateObj = new Date(parseInt(y), parseInt(m) - 1, 1);
        monthTitle.innerText = dateObj.toLocaleString('en-US', { month: 'long', year: 'numeric' });
    }

    const habits = data.habits || [];
    const logs = data.logs || {};
    const [year, month] = currentHabitMonth.split('-').map(Number);
    const totalDays = new Date(year, month, 0).getDate();
    
    // Render Header Days (Day abbreviation + Day number)
    const dayNames = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
    let headerHtml = '<th class="habit-col-hdr">Habit</th>';
    
    for (let d = 1; d <= totalDays; d++) {
        const dateObj = new Date(year, month - 1, d);
        const dayAbb = dayNames[dateObj.getDay()];
        const isToday = (d === 24 && month === 9 && year === 2026); // Match screenshot date
        headerHtml += `
            <th>
                <div class="day-hdr-day">${dayAbb}</div>
                <div class="day-hdr-num ${isToday ? 'today' : ''}">${d}</div>
            </th>
        `;
    }
    document.getElementById('gwTrackerTableHeader').innerHTML = headerHtml;

    // Render Habit Rows
    let rowsHtml = '';
    habits.forEach(h => {
        const hid = h.habit_id;
        const habitLogs = logs[hid] || {};
        
        rowsHtml += `
            <tr>
                <td class="habit-col-cell">
                    <div class="habit-name-flex">
                        <span class="habit-icon">${h.icon}</span>
                        <span>${h.name}</span>
                    </div>
                </td>
        `;
        
        for (let d = 1; d <= totalDays; d++) {
            const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
            const isChecked = habitLogs[dateStr] === 1;
            
            rowsHtml += `
                <td>
                    <div class="check-tile ${isChecked ? 'checked' : ''}" 
                         onclick="toggleCheckTile(${hid}, '${dateStr}')">
                        ${isChecked ? '✓' : ''}
                    </div>
                </td>
            `;
        }
        rowsHtml += '</tr>';
    });
    
    document.getElementById('gwTrackerTableBody').innerHTML = rowsHtml;
}

async function toggleCheckTile(habitId, dateStr) {
    try {
        const res = await fetch('/api/habits/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ habit_id: habitId, date: dateStr })
        });
        const data = await res.json();
        if (data.success) {
            fetchAndRenderTracker();
        }
    } catch (e) {
        console.error("Error toggling habit log:", e);
    }
}

function updateDoneTodayBadge(data) {
    const badge = document.getElementById('gwDoneTodayBadge');
    if (!badge) return;

    const habits = data.habits || [];
    const logs = data.logs || {};
    const todayStr = '2026-09-24';
    
    let completedToday = 0;
    habits.forEach(h => {
        if (logs[h.habit_id] && logs[h.habit_id][todayStr] === 1) {
            completedToday++;
        }
    });
    
    const pct = habits.length > 0 ? Math.round((completedToday / habits.length) * 100) : 0;
    badge.innerText = `${pct}% done today`;
}

function changeMonth(delta) {
    const [y, m] = currentHabitMonth.split('-').map(Number);
    let newM = m + delta;
    let newY = y;
    if (newM > 12) { newM = 1; newY++; }
    if (newM < 1) { newM = 12; newY--; }
    
    currentHabitMonth = `${newY}-${String(newM).padStart(2, '0')}`;
    if (activeGwSubTab === 'tracker') fetchAndRenderTracker();
    if (activeGwSubTab === 'calendar') fetchAndRenderCalendar();
}

function goToTodayMonth() {
    currentHabitMonth = '2026-09';
    selectedCalDate = '2026-09-24';
    if (activeGwSubTab === 'tracker') fetchAndRenderTracker();
    if (activeGwSubTab === 'calendar') fetchAndRenderCalendar();
}

function cycleEmojiSelector() {
    selectedEmojiIndex = (selectedEmojiIndex + 1) % EMOJI_LIST.length;
    document.getElementById('gwEmojiSelectBtn').innerText = EMOJI_LIST[selectedEmojiIndex];
}

async function handleAddHabitSubmit(e) {
    e.preventDefault();
    const input = document.getElementById('gwAddHabitInput');
    const name = input.value.trim();
    if (!name) return;

    const icon = EMOJI_LIST[selectedEmojiIndex];
    try {
        const res = await fetch('/api/habits', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name, icon: icon })
        });
        const data = await res.json();
        if (data.success) {
            input.value = '';
            showToast(`Added habit: ${icon} ${name}`, 'success');
            fetchAndRenderTracker();
        }
    } catch (err) {
        showToast('Error adding habit', 'error');
    }
}

/* CALENDAR HEATMAP VIEW */
async function fetchAndRenderCalendar() {
    try {
        const res = await fetch(`/api/habits?month=${currentHabitMonth}`);
        const result = await res.json();
        if (result.success) {
            renderCalendarGrid(result.data);
            renderDayDetailPanel(result.data, selectedCalDate);
        }
    } catch (e) {
        console.error("Error loading calendar data:", e);
    }
}

function renderCalendarGrid(data) {
    const [year, month] = currentHabitMonth.split('-').map(Number);
    const totalDays = new Date(year, month, 0).getDate();
    const firstDayIdx = new Date(year, month - 1, 1).getDay(); // 0 = Sun
    
    const habits = data.habits || [];
    const logs = data.logs || {};
    const totalHabits = habits.length;

    let gridHtml = '';
    // Empty padding tiles for previous month
    for (let p = 0; p < firstDayIdx; p++) {
        gridHtml += '<div class="cal-day-tile" style="visibility:hidden;"></div>';
    }

    for (let d = 1; d <= totalDays; d++) {
        const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
        
        // Compute daily completion count
        let completedCount = 0;
        habits.forEach(h => {
            if (logs[h.habit_id] && logs[h.habit_id][dateStr] === 1) completedCount++;
        });

        const pct = totalHabits > 0 ? completedCount / totalHabits : 0;
        let lvl = 'lvl-0';
        if (pct > 0 && pct <= 0.25) lvl = 'lvl-1';
        else if (pct > 0.25 && pct <= 0.5) lvl = 'lvl-2';
        else if (pct > 0.5 && pct <= 0.75) lvl = 'lvl-3';
        else if (pct > 0.75) lvl = 'lvl-4';

        const isSelected = (dateStr === selectedCalDate);

        gridHtml += `
            <div class="cal-day-tile ${lvl} ${isSelected ? 'selected' : ''}" 
                 onclick="selectCalendarDate('${dateStr}')">
                ${d}
            </div>
        `;
    }

    document.getElementById('gwCalendarGridMatrix').innerHTML = gridHtml;
}

function selectCalendarDate(dateStr) {
    selectedCalDate = dateStr;
    fetchAndRenderCalendar();
}

function renderDayDetailPanel(data, dateStr) {
    const panel = document.getElementById('gwDayDetailPanel');
    if (!panel) return;

    const [y, m, d] = dateStr.split('-');
    const dateObj = new Date(parseInt(y), parseInt(m) - 1, parseInt(d));
    const dateTitle = dateObj.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });

    const habits = data.habits || [];
    const logs = data.logs || {};

    let html = `
        <h3 style="font-family:'Playfair Display',serif;font-size:1.5rem;color:#f2efe6;margin-bottom:0.5rem;">${dateTitle}</h3>
        <p style="font-size:0.85rem;color:#949a88;margin-bottom:1.5rem;">View and toggle habits for this specific day.</p>
        <div style="display:flex;flex-direction:column;gap:0.75rem;">
    `;

    habits.forEach(h => {
        const hid = h.habit_id;
        const isChecked = logs[hid] && logs[hid][dateStr] === 1;

        html += `
            <div style="display:flex;align-items:center;justify-content:space-between;background:#1c2016;border:1px solid #282e20;padding:0.85rem 1.1rem;border-radius:10px;">
                <div class="habit-name-flex">
                    <span>${h.icon}</span>
                    <span>${h.name}</span>
                </div>
                <div class="check-tile ${isChecked ? 'checked' : ''}" onclick="toggleCheckTile(${hid}, '${dateStr}')">
                    ${isChecked ? '✓' : ''}
                </div>
            </div>
        `;
    });

    html += '</div>';
    panel.innerHTML = html;
}

/* ANALYSIS VIEW */
async function fetchAndRenderAnalysis() {
    try {
        const res = await fetch(`/api/habits/analysis?filter=${analysisFilterType}&month=${currentHabitMonth}`);
        const result = await res.json();
        if (result.success) {
            renderAnalysisDashboard(result.analysis);
        }
    } catch (e) {
        console.error("Error loading analysis data:", e);
    }
}

function switchAnalysisFilter(filterType) {
    analysisFilterType = filterType;
    document.getElementById('gwFilterMonthBtn').classList.toggle('active', filterType === 'month');
    document.getElementById('gwFilterYearBtn').classList.toggle('active', filterType === 'year');
    fetchAndRenderAnalysis();
}

function renderAnalysisDashboard(an) {
    // 1. Metric Cards
    document.getElementById('gwOverallPctVal').innerText = `${an.overall_completion_pct}%`;
    document.getElementById('gwHabitDaysLoggedVal').innerText = an.habit_days_logged;
    document.getElementById('gwStreakVal').innerText = an.longest_active_streak;
    document.getElementById('gwHabitsTrackedVal').innerText = an.habits_tracked;

    document.getElementById('gwCompletionSectionTitle').innerText = `Completion this ${an.timeframe} — ${an.period_label}`;

    // 2. Progress Bars
    let progressHtml = '';
    an.habit_progress.forEach(h => {
        progressHtml += `
            <div class="progress-habit-row">
                <div class="progress-habit-lbl">
                    <span>${h.icon}</span>
                    <span>${h.name}</span>
                </div>
                <div class="progress-track-gw">
                    <div class="progress-fill-gw" style="width: ${h.completion_pct}%;"></div>
                </div>
                <div class="progress-pct-lbl">${h.completion_pct}%</div>
            </div>
        `;
    });
    document.getElementById('gwAnalysisProgressContainer').innerHTML = progressHtml;

    // 3. Needs Attention Section
    let needsHtml = '';
    if (an.needs_attention && an.needs_attention.length > 0) {
        an.needs_attention.forEach(n => {
            needsHtml += `
                <div class="needs-attention-card">
                    <span style="font-size:1.5rem;">${n.icon}</span>
                    <div>
                        <div class="needs-attention-title">${n.name}</div>
                        <div class="needs-attention-desc">${n.message}</div>
                    </div>
                </div>
            `;
        });
    } else {
        needsHtml = '<p style="font-size:0.85rem;color:#8c9480;">Great job! No habits require critical attention right now.</p>';
    }
    document.getElementById('gwNeedsAttentionContainer').innerHTML = needsHtml;

    // 4. Daily Completion Bar Matrix Chart (Screenshot Chart 1)
    const dailyContainer = document.getElementById('gwDailyCompletionBarContainer');
    if (dailyContainer && an.daily_completion_counts) {
        let dailyHtml = '<div style="display:flex;align-items:flex-end;gap:4px;height:120px;padding-top:20px;">';
        const maxVal = Math.max(...Object.values(an.daily_completion_counts), 4);
        
        for (let d = 1; d <= 30; d++) {
            const cnt = an.daily_completion_counts[d] || 0;
            const heightPct = (cnt / maxVal) * 100;
            const barBg = cnt > 0 ? '#32472d' : 'rgba(255,255,255,0.03)';
            const isToday = (d === 24);

            dailyHtml += `
                <div style="flex:1;display:flex;flex-direction:column;align-items:center;height:100%;justify-content:flex-end;">
                    <div style="width:100%;height:${Math.max(heightPct, 4)}%;background:${barBg};border-radius:3px;${isToday ? 'border-top:2px solid #6b9071;' : ''}"></div>
                    <div style="font-size:0.65rem;color:${isToday ? '#6b9071;font-weight:bold;' : '#64748b;'}margin-top:6px;">${d}</div>
                </div>
            `;
        }
        dailyHtml += '</div>';
        dailyContainer.innerHTML = dailyHtml;
    }

    // 5. Habit Share Doughnut Chart & Legend (Screenshot Chart 2)
    const shareLegendContainer = document.getElementById('gwHabitShareLegendContainer');
    if (shareLegendContainer && an.habit_shares) {
        const activeShares = an.habit_shares.filter(s => s.share_pct > 0);
        const palette = ['#597d5f', '#d97706', '#3b82f6', '#9333ea', '#ec4899', '#10b981'];

        let legendHtml = '<div style="display:flex;flex-direction:column;gap:0.75rem;">';
        const labels = [];
        const dataVals = [];
        const bgColors = [];

        if (activeShares.length > 0) {
            activeShares.forEach((s, idx) => {
                const color = palette[idx % palette.length];
                labels.push(`${s.icon} ${s.name}`);
                dataVals.push(s.share_pct);
                bgColors.push(color);

                legendHtml += `
                    <div style="display:flex;align-items:center;justify-content:space-between;font-size:0.9rem;">
                        <div style="display:flex;align-items:center;gap:0.75rem;">
                            <span style="width:12px;height:12px;border-radius:3px;background:${color};display:inline-block;"></span>
                            <span>${s.icon} ${s.name}</span>
                        </div>
                        <strong style="color:#a8b298;">${s.share_pct}%</strong>
                    </div>
                `;
            });
        } else {
            legendHtml += '<p style="font-size:0.85rem;color:#8c9480;">No check-in data logged yet this month.</p>';
        }

        legendHtml += '</div>';
        shareLegendContainer.innerHTML = legendHtml;

        // Render Chart.js Doughnut if canvas exists
        const canvas = document.getElementById('gwHabitShareDoughnutCanvas');
        if (canvas && activeShares.length > 0) {
            if (window.gwDoughnutInstance) window.gwDoughnutInstance.destroy();
            const ctx = canvas.getContext('2d');
            window.gwDoughnutInstance = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: dataVals,
                        backgroundColor: bgColors,
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '70%',
                    plugins: { legend: { display: false } }
                }
            });
        }
    }
}


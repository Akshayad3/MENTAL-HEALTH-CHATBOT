// Report Processing and Upload Client JS

document.addEventListener('DOMContentLoaded', () => {
    initReportUploadForm();
});

function initReportUploadForm() {
    const form = document.getElementById('reportUploadForm');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fileInput = document.getElementById('reportFileInput');
            if (!fileInput.files || fileInput.files.length === 0) {
                showToast('Please select a PDF, DOCX, or Image file to upload.', 'error');
                return;
            }

            const formData = new FormData();
            formData.append('report_file', fileInput.files[0]);

            const submitBtn = document.getElementById('reportSubmitBtn');
            submitBtn.innerText = 'Analyzing Report with NLP...';
            submitBtn.disabled = true;

            try {
                const res = await fetch('/api/reports/upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                submitBtn.innerText = 'Upload & Analyze Report';
                submitBtn.disabled = false;

                if (data.success) {
                    showToast('Report uploaded & analyzed successfully!', 'success');
                    renderReportSummaryView(data.summary_data);
                    window.loadUserReports();
                } else {
                    showToast(data.message || 'Report processing failed', 'error');
                }
            } catch (err) {
                submitBtn.innerText = 'Upload & Analyze Report';
                submitBtn.disabled = false;
                showToast('Error uploading report file', 'error');
            }
        });
    }
}

window.loadUserReports = async function() {
    try {
        const res = await fetch('/api/reports/history');
        const data = await res.json();
        if (data.success) {
            renderReportsHistoryTable(data.reports);
        }
    } catch (e) {
        console.error("Error loading reports history:", e);
    }
};

function renderReportSummaryView(summary) {
    const resultCard = document.getElementById('reportAnalysisResultCard');
    if (!resultCard) return;

    resultCard.style.display = 'block';

    document.getElementById('repDocTitle').innerText = summary.document_name;
    document.getElementById('repSummaryText').innerText = summary.summary_text;

    // Key Findings
    const findingsList = document.getElementById('repFindingsList');
    findingsList.innerHTML = summary.key_findings.map(f => `<li>🔍 ${f}</li>`).join('');

    // Important Observations
    const obsList = document.getElementById('repObservationsList');
    obsList.innerHTML = summary.important_observations.map(o => `<li>📋 ${o}</li>`).join('');

    // Recommendations Mentioned
    const recsList = document.getElementById('repRecommendationsList');
    recsList.innerHTML = summary.recommendations_mentioned.map(r => `<li>💡 ${r}</li>`).join('');

    // Medication Info
    const medContainer = document.getElementById('repMedicationContainer');
    const medInfo = summary.medication_info;

    if (medInfo.found && medInfo.medications.length > 0) {
        let html = `
            <div style="background:rgba(245,158,11,0.08);border:1px solid var(--status-warning);padding:1rem;border-radius:var(--radius-sm);margin-top:1rem;">
                <h4 style="color:var(--status-warning);margin-bottom:0.5rem;">💊 MEDICATIONS MENTIONED IN REPORT</h4>
                <table class="metrics-table">
                    <thead>
                        <tr><th>Medication Name</th><th>Dosage</th><th>Frequency</th><th>Purpose</th></tr>
                    </thead>
                    <tbody>
        `;
        medInfo.medications.forEach(m => {
            html += `<tr><td><strong>${m.name}</strong></td><td>${m.dosage}</td><td>${m.frequency}</td><td>${m.purpose}</td></tr>`;
        });
        html += `
                    </tbody>
                </table>
                <p style="font-size:0.775rem;color:var(--text-muted);margin-top:0.75rem;">⚠️ <strong>STRICT DISCLAIMER:</strong> ${medInfo.disclaimer}</p>
            </div>
        `;
        medContainer.innerHTML = html;
    } else {
        medContainer.innerHTML = `
            <div style="background:rgba(255,255,255,0.03);padding:0.85rem;border-radius:var(--radius-sm);margin-top:1rem;font-size:0.85rem;color:var(--text-muted);">
                ℹ️ <strong>No medication information was identified in this document.</strong>
            </div>
        `;
    }
}

function renderReportsHistoryTable(reports) {
    const tableBody = document.getElementById('reportsHistoryTableBody');
    if (!tableBody) return;

    if (!reports || reports.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="3" style="text-align:center;color:var(--text-muted);">No reports uploaded yet.</td></tr>';
        return;
    }

    let html = '';
    reports.forEach(r => {
        html += `
            <tr>
                <td><strong>📄 ${r.filename}</strong></td>
                <td><span style="font-size:0.85rem;color:var(--text-muted);">${r.summary.substring(0, 80)}...</span></td>
                <td>${new Date(r.uploaded_at).toLocaleDateString()}</td>
            </tr>
        `;
    });
    tableBody.innerHTML = html;
}

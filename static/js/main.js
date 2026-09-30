// Main SPA Navigation, Routing and General Utilities

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initAccountDeletionModal();
});

function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link[data-view]');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetView = link.dataset.view;
            switchView(targetView);
        });
    });
}

function switchView(viewId) {
    // Hide all view sections
    const views = document.querySelectorAll('.view-section');
    views.forEach(v => v.style.display = 'none');

    // Remove active class from nav links
    const navLinks = document.querySelectorAll('.nav-link[data-view]');
    navLinks.forEach(l => l.classList.remove('active'));

    // Show target view
    const targetElement = document.getElementById(`view-${viewId}`);
    if (targetElement) {
        targetElement.style.display = 'block';
    }

    // Highlight active link
    const activeLink = document.querySelector(`.nav-link[data-view="${viewId}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }

    // Trigger view specific load handlers
    if (viewId === 'dashboard') window.loadDashboardData();
    if (viewId === 'chat') window.initChatView();
    if (viewId === 'reports') window.loadUserReports();
    if (viewId === 'assessments') window.loadAssessmentsView();
    if (viewId === 'trends') window.loadTrendsView();
    if (viewId === 'recommendations') window.loadRecommendationsView();
    if (viewId === 'evaluation') window.loadEvaluationView();
    if (viewId === 'habits') window.loadHabitsView();
}

function showToast(message, type = 'info') {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:99999;display:flex;flex-direction:column;gap:10px;';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.style.cssText = `
        padding: 12px 20px;
        border-radius: 8px;
        background: #121a2f;
        color: #fff;
        font-size: 0.9rem;
        border: 1px solid ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#38bdf8'};
        box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        animation: fadeIn 0.3s ease;
    `;
    toast.innerText = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 4000);
}

function initAccountDeletionModal() {
    const deleteBtn = document.getElementById('deleteAccountBtn');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', async () => {
            if (confirm("Are you sure you want to permanently delete your account and all associated mental health records, conversation history, and uploaded reports? This action CANNOT be undone.")) {
                try {
                    const res = await fetch('/api/account/delete', { method: 'POST' });
                    const data = await res.json();
                    if (data.success) {
                        showToast('Account and all data permanently deleted.', 'info');
                        logoutUser();
                    } else {
                        showToast(data.message || 'Failed to delete account', 'error');
                    }
                } catch (e) {
                    showToast('Error executing account deletion', 'error');
                }
            }
        });
    }
}

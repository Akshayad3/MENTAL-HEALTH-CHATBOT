// Authentication Management Client JS

document.addEventListener('DOMContentLoaded', () => {
    initAuthTabs();
    initAuthForms();
    checkAuthSession();
});

function initAuthTabs() {
    const tabBtns = document.querySelectorAll('.auth-tab-btn');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            if (btn.dataset.tab === 'login') {
                loginForm.style.display = 'block';
                registerForm.style.display = 'none';
            } else {
                loginForm.style.display = 'none';
                registerForm.style.display = 'block';
            }
        });
    });
}

function initAuthForms() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const googleLoginBtn = document.getElementById('googleLoginBtn');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;

            try {
                const res = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                const data = await res.json();
                if (data.success) {
                    showToast('Welcome back! Logging in...', 'success');
                    window.currentUser = data.user;
                    hideAuthOverlay();
                    window.loadDashboardData();
                } else {
                    showToast(data.message || 'Login failed', 'error');
                }
            } catch (err) {
                showToast('Server communication error', 'error');
            }
        });
    }

    const forgotForm = document.getElementById('forgotPasswordForm');
    if (forgotForm) {
        forgotForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('resetEmail').value;
            const new_password = document.getElementById('resetNewPassword').value;

            try {
                const res = await fetch('/api/auth/reset-password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, new_password })
                });
                const data = await res.json();
                if (data.success) {
                    showToast('Password reset successfully!', 'success');
                    window.currentUser = data.user;
                    hideAuthOverlay();
                    window.loadDashboardData();
                } else {
                    showToast(data.message || 'Password reset failed', 'error');
                }
            } catch (err) {
                showToast('Server communication error during password reset', 'error');
            }
        });
    }


    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('regName').value;
            const email = document.getElementById('regEmail').value;
            const password = document.getElementById('regPassword').value;

            try {
                const res = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, password })
                });
                const data = await res.json();
                if (data.success) {
                    showToast('Account created successfully!', 'success');
                    window.currentUser = data.user;
                    hideAuthOverlay();
                    window.loadDashboardData();
                } else {
                    showToast(data.message || 'Registration failed', 'error');
                }
            } catch (err) {
                showToast('Server communication error', 'error');
            }
        });
    }

    if (googleLoginBtn) {
        googleLoginBtn.addEventListener('click', async () => {
            // Simulated secure Google OAuth / OpenID Connect handler
            const mockGoogleUser = {
                google_id: "google_1098237461928374",
                name: "Research Student User",
                email: "student.nlp.researcher@gmail.com"
            };

            try {
                const res = await fetch('/api/auth/google', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(mockGoogleUser)
                });
                const data = await res.json();
                if (data.success) {
                    showToast('Google Authentication Successful!', 'success');
                    window.currentUser = data.user;
                    hideAuthOverlay();
                    window.loadDashboardData();
                } else {
                    showToast(data.message || 'Google Auth failed', 'error');
                }
            } catch (err) {
                showToast('Google OAuth error', 'error');
            }
        });
    }
}

async function checkAuthSession() {
    try {
        const res = await fetch('/api/auth/me');
        const data = await res.json();
        if (data.authenticated) {
            window.currentUser = data.user;
            hideAuthOverlay();
            window.loadDashboardData();
        } else {
            showAuthOverlay();
        }
    } catch (e) {
        showAuthOverlay();
    }
}

function showAuthOverlay() {
    document.getElementById('authOverlay').style.display = 'flex';
    document.getElementById('appWrapper').style.display = 'none';
}

function hideAuthOverlay() {
    document.getElementById('authOverlay').style.display = 'none';
    document.getElementById('appWrapper').style.display = 'flex';
    updateUserProfileDisplay();
}

function updateUserProfileDisplay() {
    if (window.currentUser) {
        document.getElementById('navUserName').innerText = window.currentUser.name;
        document.getElementById('navUserEmail').innerText = window.currentUser.email;
        document.getElementById('userAvatarInitial').innerText = window.currentUser.name.charAt(0).toUpperCase();
        
        const gwName = document.getElementById('gwWelcomeUserName');
        if (gwName) gwName.innerText = window.currentUser.name.toLowerCase();
    }
}

async function logoutUser() {
    await fetch('/api/auth/logout', { method: 'POST' });
    window.currentUser = null;
    showAuthOverlay();
    showToast('Logged out successfully', 'info');
}

function showForgotPasswordForm(e) {
    if (e) e.preventDefault();
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'none';
    document.getElementById('forgotPasswordForm').style.display = 'block';
    const authTabs = document.querySelector('.auth-tabs');
    if (authTabs) authTabs.style.display = 'none';
}

function showLoginFormFromReset(e) {
    if (e) e.preventDefault();
    document.getElementById('forgotPasswordForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'none';
    document.getElementById('loginForm').style.display = 'block';
    const authTabs = document.querySelector('.auth-tabs');
    if (authTabs) authTabs.style.display = 'flex';
}


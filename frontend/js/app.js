document.addEventListener("DOMContentLoaded", () => {
    // Landing & Feature Selection Elements
    const featureSelectionLanding = document.getElementById("featureSelectionLanding");
    const selectFeatureBtns = document.querySelectorAll(".select-feature-btn");
    const activeModeBadge = document.getElementById("activeModeBadge");
    const activeModeText = document.getElementById("activeModeText");
    const switchModeBtn = document.getElementById("switchModeBtn");
    const socialLinksGroup = document.getElementById("socialLinksGroup");
    const tailorActionsGroup = document.getElementById("tailorActionsGroup");
    const step2Title = document.getElementById("step2Title");
    const step2Desc = document.getElementById("step2Desc");
    const emptyStateTitle = document.getElementById("emptyStateTitle");
    const emptyStateDesc = document.getElementById("emptyStateDesc");

    // DOM Elements
    const uploadForm = document.getElementById("uploadForm");
    const fileInput = document.getElementById("resumeFileInput");
    const fileNameDisplay = document.getElementById("fileNameDisplay");
    const activeResumeBadge = document.getElementById("activeResumeBadge");
    const activeResumeName = document.getElementById("activeResumeName");
    const deleteResumeBtn = document.getElementById("deleteResumeBtn");
    const uploadBtn = document.getElementById("uploadBtn");
    
    const tailorForm = document.getElementById("tailorForm");
    const submitMatchBtn = document.getElementById("submitMatchBtn");
    const submitTailorBtn = document.getElementById("submitTailorBtn");
    const historyBtn = document.getElementById("historyBtn");
    const historyContainer = document.getElementById("historyContainer");
    const historyList = document.getElementById("historyList");
    const temperatureRange = document.getElementById("temperatureRange");
    const tempValue = document.getElementById("tempValue");

    // Canvas & View Containers
    const emptyState = document.getElementById("emptyState");
    const shimmerLoader = document.getElementById("shimmerLoader");
    const paperContent = document.getElementById("paperContent");
    const renderedDocumentOutput = document.getElementById("renderedDocumentOutput");
    const matchAnalysisCard = document.getElementById("matchAnalysisCard");
    
    // Feature 1 Match Analyzer Elements
    const matchGaugeValue = document.getElementById("matchGaugeValue");
    const keywordsText = document.getElementById("keywordsText");
    const matchProgressBar = document.getElementById("matchProgressBar");
    const skillsMatchedContainer = document.getElementById("skillsMatchedContainer");
    const skillsMissingContainer = document.getElementById("skillsMissingContainer");
    const recommendationsList = document.getElementById("recommendationsList");

    // Tab buttons
    const tabMatchBtn = document.getElementById("tabMatchBtn");
    const tabTailorBtn = document.getElementById("tabTailorBtn");

    const scoresWidget = document.getElementById("scoresWidget");
    const beforeScoreValue = document.getElementById("beforeScoreValue");
    const afterScoreValue = document.getElementById("afterScoreValue");
    const analysisNoteCard = document.getElementById("analysisNoteCard");
    const analysisNoteText = document.getElementById("analysisNoteText");
    
    const downloadPdfBtn = document.getElementById("downloadPdfBtn");
    const downloadDocxBtn = document.getElementById("downloadDocxBtn");
    const copyBtn = document.getElementById("copyBtn");
    const toastContainer = document.getElementById("toastContainer");

    // Theme Elements
    const themeToggleBtn = document.getElementById("themeToggleBtn");
    const landingThemeToggleBtn = document.getElementById("landingThemeToggleBtn");
    const sunIcon = document.getElementById("sunIcon");
    const moonIcon = document.getElementById("moonIcon");
    const sunIconLanding = document.querySelector(".sunIconLanding");
    const moonIconLanding = document.querySelector(".moonIconLanding");

    // Auth Elements (Main Header & Landing Header)
    const loginBtn = document.getElementById("loginBtn");
    const demoLoginBtn = document.getElementById("demoLoginBtn");
    const logoutBtn = document.getElementById("logoutBtn");
    const userProfile = document.getElementById("userProfile");
    const userAvatar = document.getElementById("userAvatar");
    const userName = document.getElementById("userName");

    const landingLoginBtn = document.getElementById("landingLoginBtn");
    const landingDemoLoginBtn = document.getElementById("landingDemoLoginBtn");
    const landingLogoutBtn = document.getElementById("landingLogoutBtn");
    const landingUserProfile = document.getElementById("landingUserProfile");
    const landingUserAvatar = document.getElementById("landingUserAvatar");
    const landingUserName = document.getElementById("landingUserName");

    let currentTailoredId = null;
    let rawTailoredMarkdown = "";
    let isAuthenticated = false;
    let currentAnalysisData = null;
    let activeFeatureMode = null; // 'match' or 'tailor'
    
    // Dynamic API Base URL & Authenticated Fetch Helper
    const getApiBaseUrl = () => {
        if (window.location.protocol === "file:") return "http://127.0.0.1:8000";
        if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
            if (window.location.port && window.location.port !== "8000") {
                return `${window.location.protocol}//${window.location.hostname}:8000`;
            }
        }
        return "";
    };
    const API_BASE = getApiBaseUrl();

    async function apiFetch(endpoint, options = {}) {
        const url = endpoint.startsWith("http") ? endpoint : `${API_BASE}${endpoint}`;
        const defaultOptions = {
            credentials: "include"
        };
        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...(options.headers || {})
            }
        };
        return fetch(url, mergedOptions);
    }
    
    // Initialize Theme (Default Dark)
    initTheme();

    function initTheme() {
        const savedTheme = localStorage.getItem("resume_aligner_theme") || "dark";
        setTheme(savedTheme);
    }

    function setTheme(theme) {
        if (theme === "light") {
            document.body.setAttribute("data-theme", "light");
            sunIcon?.classList.remove("hidden");
            moonIcon?.classList.add("hidden");
            sunIconLanding?.classList.remove("hidden");
            moonIconLanding?.classList.add("hidden");
        } else {
            document.body.removeAttribute("data-theme");
            sunIcon?.classList.add("hidden");
            moonIcon?.classList.remove("hidden");
            sunIconLanding?.classList.add("hidden");
            moonIconLanding?.classList.remove("hidden");
        }
        localStorage.setItem("resume_aligner_theme", theme);
    }

    function toggleTheme() {
        const currentTheme = document.body.getAttribute("data-theme") === "light" ? "light" : "dark";
        const newTheme = currentTheme === "dark" ? "light" : "dark";
        setTheme(newTheme);
        showToast(`Switched to ${newTheme} mode`, "info", "Theme Preference");
    }

    themeToggleBtn?.addEventListener("click", toggleTheme);
    landingThemeToggleBtn?.addEventListener("click", toggleTheme);

    // Handle Landing Screen Feature Card Selection - Direct Transition to Workspace
    selectFeatureBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const feature = btn.getAttribute("data-feature");
            enterWorkspace(feature);
        });
    });

    // Switch Feature Mode Button
    switchModeBtn?.addEventListener("click", () => {
        featureSelectionLanding?.classList.remove("fade-out");
        activeModeBadge?.classList.add("hidden");
    });

    function enterWorkspace(feature) {
        activeFeatureMode = feature;
        featureSelectionLanding?.classList.add("fade-out");
        activeModeBadge?.classList.remove("hidden");

        if (feature === "match") {
            if (activeModeText) activeModeText.textContent = "Mode: Match Analyzer";
            if (step2Title) step2Title.textContent = "Match Requirements";
            if (step2Desc) step2Desc.textContent = "Enter target role and job post to analyze skill gaps & match score.";
            
            socialLinksGroup?.classList.add("hidden");
            submitMatchBtn?.classList.remove("hidden");
            submitTailorBtn?.classList.add("hidden");
            tailorActionsGroup?.classList.add("hidden");
            
            tabMatchBtn?.classList.remove("hidden");
            tabTailorBtn?.classList.add("hidden");
            tabMatchBtn?.click();

            if (emptyStateTitle) emptyStateTitle.textContent = "Match Analyzer Ready";
            if (emptyStateDesc) emptyStateDesc.textContent = "Upload master resume & enter target job description, then click 'Analyze Match Score'.";

            if (currentAnalysisData) {
                emptyState?.classList.add("hidden");
                matchAnalysisCard?.classList.remove("hidden");
            } else {
                emptyState?.classList.remove("hidden");
                matchAnalysisCard?.classList.add("hidden");
            }

        } else if (feature === "tailor") {
            if (activeModeText) activeModeText.textContent = "Mode: Resume Tailor";
            if (step2Title) step2Title.textContent = "Tailoring Requirements";
            if (step2Desc) step2Desc.textContent = "Provide job description and social links to tailor your ATS resume.";

            socialLinksGroup?.classList.remove("hidden");
            submitMatchBtn?.classList.add("hidden");
            submitTailorBtn?.classList.remove("hidden");
            tailorActionsGroup?.classList.remove("hidden");

            tabMatchBtn?.classList.add("hidden");
            tabTailorBtn?.classList.remove("hidden");
            tabTailorBtn?.click();

            if (emptyStateTitle) emptyStateTitle.textContent = "Resume Tailor Ready";
            if (emptyStateDesc) emptyStateDesc.textContent = "Upload master resume, fill target job info, and click 'Tailor Resume with AI'.";

            if (rawTailoredMarkdown) {
                emptyState?.classList.add("hidden");
                paperContent?.classList.remove("hidden");
            } else {
                emptyState?.classList.remove("hidden");
                paperContent?.classList.add("hidden");
            }
        }
    }

    // Custom Glassmorphic Sign-In Required Modal
    function showCustomAuthModal(title, message) {
        const modal = document.getElementById("customAuthModal");
        const titleEl = document.getElementById("authModalTitle");
        const msgEl = document.getElementById("authModalMessage");
        const cancelBtn = document.getElementById("authCancelBtn");
        const confirmBtn = document.getElementById("authConfirmBtn");
        const demoBtn = document.getElementById("authDemoBtn");

        if (!modal) {
            window.location.href = `${API_BASE}/api/v1/auth/login`;
            return;
        }

        if (titleEl) titleEl.textContent = title;
        if (msgEl) msgEl.textContent = message;

        modal.classList.remove("hidden");

        const cleanup = () => {
            modal.classList.add("hidden");
            cancelBtn?.removeEventListener("click", onCancel);
            confirmBtn?.removeEventListener("click", onConfirm);
            demoBtn?.removeEventListener("click", onDemo);
        };

        const onCancel = () => {
            cleanup();
        };

        const onConfirm = () => {
            cleanup();
            window.location.href = `${API_BASE}/api/v1/auth/login`;
        };

        const onDemo = () => {
            cleanup();
            window.location.href = `${API_BASE}/api/v1/auth/demo-login`;
        };

        cancelBtn?.addEventListener("click", onCancel);
        confirmBtn?.addEventListener("click", onConfirm);
        demoBtn?.addEventListener("click", onDemo);
    }

    // Custom Glassmorphic Confirmation Modal Helper
    function showCustomConfirm(title, message) {
        return new Promise((resolve) => {
            const modal = document.getElementById("customConfirmModal");
            const titleEl = document.getElementById("modalTitle");
            const msgEl = document.getElementById("modalMessage");
            const cancelBtn = document.getElementById("modalCancelBtn");
            const confirmBtn = document.getElementById("modalConfirmBtn");

            if (!modal) return resolve(window.confirm(message));

            if (titleEl) titleEl.textContent = title;
            if (msgEl) msgEl.textContent = message;

            modal.classList.remove("hidden");

            const cleanup = () => {
                modal.classList.add("hidden");
                cancelBtn.removeEventListener("click", onCancel);
                confirmBtn.removeEventListener("click", onConfirm);
            };

            const onCancel = () => {
                cleanup();
                resolve(false);
            };

            const onConfirm = () => {
                cleanup();
                resolve(true);
            };

            cancelBtn.addEventListener("click", onCancel);
            confirmBtn.addEventListener("click", onConfirm);
        });
    }

    // Custom Glassmorphic Alert Modal Helper
    function showCustomAlert(title, message, type = "error") {
        return new Promise((resolve) => {
            const modal = document.getElementById("customAlertModal");
            const iconBadge = document.getElementById("alertIconBadge");
            const titleEl = document.getElementById("alertModalTitle");
            const msgEl = document.getElementById("alertModalMessage");
            const okBtn = document.getElementById("alertModalOkBtn");

            if (!modal) {
                showToast(message, type, title);
                return resolve();
            }

            if (titleEl) titleEl.textContent = title;
            if (msgEl) msgEl.textContent = message;

            if (iconBadge) {
                iconBadge.className = `modal-icon-badge ${type}`;
                if (type === "error") {
                    iconBadge.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;
                } else if (type === "success") {
                    iconBadge.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
                } else {
                    iconBadge.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;
                }
            }

            modal.classList.remove("hidden");

            const onDismiss = () => {
                modal.classList.add("hidden");
                okBtn.removeEventListener("click", onDismiss);
                resolve();
            };

            okBtn.addEventListener("click", onDismiss);
        });
    }

    // Check Auth Status on Load
    checkAuthStatus();

    async function checkAuthStatus() {
        try {
            const res = await apiFetch("/api/v1/auth/me");
            if (res.ok) {
                const user = await res.json();
                isAuthenticated = true;
                loginBtn?.classList.add("hidden");
                demoLoginBtn?.classList.add("hidden");
                userProfile?.classList.remove("hidden");

                landingLoginBtn?.classList.add("hidden");
                landingDemoLoginBtn?.classList.add("hidden");
                landingUserProfile?.classList.remove("hidden");

                const nameOrEmail = user.name || user.email || "User";
                if (userName) userName.textContent = nameOrEmail;
                if (landingUserName) landingUserName.textContent = nameOrEmail;
                
                const avatarSvg = `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32"><rect width="32" height="32" rx="16" fill="%2306b6d4"/><text x="50%" y="54%" dominant-baseline="middle" text-anchor="middle" fill="white" font-family="sans-serif" font-weight="bold" font-size="14">${nameOrEmail.charAt(0).toUpperCase()}</text></svg>`;

                if (userAvatar) {
                    userAvatar.onerror = () => { userAvatar.src = avatarSvg; };
                    userAvatar.src = user.picture || avatarSvg;
                }
                if (landingUserAvatar) {
                    landingUserAvatar.onerror = () => { landingUserAvatar.src = avatarSvg; };
                    landingUserAvatar.src = user.picture || avatarSvg;
                }
                
                fetchActiveResume();
                fetchUsageStatus();
            } else {
                isAuthenticated = false;
                loginBtn?.classList.remove("hidden");
                demoLoginBtn?.classList.remove("hidden");
                userProfile?.classList.add("hidden");

                landingLoginBtn?.classList.remove("hidden");
                landingDemoLoginBtn?.classList.remove("hidden");
                landingUserProfile?.classList.add("hidden");
            }
        } catch (_) {
            isAuthenticated = false;
        }
    }

    let resetTimerInterval = null;

    async function fetchUsageStatus() {
        if (!isAuthenticated) return;
        try {
            const res = await apiFetch("/api/v1/tailor/usage-status");
            if (res.ok) {
                const data = await res.json();
                updateUsageUI(data);
            }
        } catch (_) {}
    }

    function updateUsageUI(data) {
        if (!data) return;
        const { match, tailor, reset_in_seconds } = data;
        const widget = document.getElementById("dailyLivesWidget");
        const matchCount = document.getElementById("matchLivesCount");
        const tailorCount = document.getElementById("tailorLivesCount");
        const matchPill = document.getElementById("matchLivesPill");
        const tailorPill = document.getElementById("tailorLivesPill");
        const resetPill = document.getElementById("resetTimerPill");

        if (widget) widget.classList.remove("hidden");

        if (matchCount) matchCount.textContent = `${match.remaining}/${match.limit}`;
        if (tailorCount) tailorCount.textContent = `${tailor.remaining}/${tailor.limit}`;

        if (matchPill) {
            if (match.remaining === 0) {
                matchPill.classList.add("exhausted");
            } else {
                matchPill.classList.remove("exhausted");
            }
        }

        if (tailorPill) {
            if (tailor.remaining === 0) {
                tailorPill.classList.add("exhausted");
            } else {
                tailorPill.classList.remove("exhausted");
            }
        }

        if (match.remaining === 0 || tailor.remaining === 0) {
            if (resetPill) resetPill.classList.remove("hidden");
            startResetCountdown(reset_in_seconds);
        } else {
            if (resetPill) resetPill.classList.add("hidden");
            if (resetTimerInterval) clearInterval(resetTimerInterval);
        }
    }

    function startResetCountdown(initialSeconds) {
        if (resetTimerInterval) clearInterval(resetTimerInterval);
        let secondsLeft = initialSeconds;

        const updateTimer = () => {
            if (secondsLeft <= 0) {
                clearInterval(resetTimerInterval);
                fetchUsageStatus();
                return;
            }
            const hrs = Math.floor(secondsLeft / 3600);
            const mins = Math.floor((secondsLeft % 3600) / 60);
            const secs = secondsLeft % 60;

            const resetText = document.getElementById("resetTimerText");
            if (resetText) {
                resetText.textContent = `Resets in ${hrs}h ${mins}m ${secs}s`;
            }
            secondsLeft--;
        };

        updateTimer();
        resetTimerInterval = setInterval(updateTimer, 1000);
    }

    const handleLogin = () => { window.location.href = `${API_BASE}/api/v1/auth/login`; };
    const handleDemoLogin = () => { window.location.href = `${API_BASE}/api/v1/auth/demo-login`; };
    const handleLogout = async () => {
        try {
            await apiFetch("/api/v1/auth/logout", { method: "POST" });
            showToast("Logged out successfully.", "success", "Signed Out");
            setTimeout(() => window.location.reload(), 1000);
        } catch (err) {
            showToast("Logout failed.", "error", "Error");
        }
    };

    loginBtn?.addEventListener("click", handleLogin);
    landingLoginBtn?.addEventListener("click", handleLogin);

    demoLoginBtn?.addEventListener("click", handleDemoLogin);
    landingDemoLoginBtn?.addEventListener("click", handleDemoLogin);

    logoutBtn?.addEventListener("click", handleLogout);
    landingLogoutBtn?.addEventListener("click", handleLogout);

    // View Tabs Switching Logic
    tabMatchBtn?.addEventListener("click", () => {
        tabMatchBtn.classList.add("active");
        tabTailorBtn?.classList.remove("active");
        
        if (currentAnalysisData) {
            emptyState?.classList.add("hidden");
            paperContent?.classList.add("hidden");
            matchAnalysisCard?.classList.remove("hidden");
        }
    });

    tabTailorBtn?.addEventListener("click", () => {
        tabTailorBtn.classList.add("active");
        tabMatchBtn?.classList.remove("active");

        if (rawTailoredMarkdown) {
            emptyState?.classList.add("hidden");
            matchAnalysisCard?.classList.add("hidden");
            paperContent?.classList.remove("hidden");
        }
    });

    // Temperature slider update
    if (temperatureRange && tempValue) {
        temperatureRange.addEventListener("input", (e) => {
            tempValue.textContent = e.target.value;
        });
    }

    // File Input Display
    fileInput?.addEventListener("change", (e) => {
        if (e.target.files.length > 0 && fileNameDisplay) {
            fileNameDisplay.textContent = e.target.files[0].name;
            showToast(`Selected file: ${e.target.files[0].name}`, "info", "File Ready");
        }
    });

    // Version History Logic (Checks auth on click)
    historyBtn?.addEventListener("click", async () => {
        if (!isAuthenticated) {
            return showCustomAuthModal("Sign In Required", "Please sign in to view version history.");
        }
        
        if (!historyContainer.classList.contains("hidden")) {
            historyContainer.classList.add("hidden");
            return;
        }

        historyBtn.disabled = true;
        historyBtn.textContent = "Loading...";

        try {
            const res = await apiFetch("/api/v1/tailor/history");
            if (!res.ok) throw new Error("Failed to fetch history");
            
            const history = await res.json();
            
            if (history.length === 0) {
                historyList.innerHTML = `<li style="font-size: 0.82rem; color: var(--text-secondary); text-align: center; padding: 0.5rem;">No history found.</li>`;
            } else {
                historyList.innerHTML = history.map(item => `
                    <li class="history-item" data-id="${item.id}" style="padding: 0.65rem 0.85rem; background: var(--canvas); border: 1px solid var(--border); border-radius: var(--radius-bubble-sm); cursor: pointer; transition: all 0.2s ease;">
                        <div style="font-size: 0.85rem; font-weight: 700; color: var(--text-primary);">${item.job_title || 'Target Role'}</div>
                        <div style="font-size: 0.75rem; color: var(--text-secondary); display: flex; justify-content: space-between; margin-top: 0.35rem;">
                            <span style="color: var(--accent-emerald); font-weight: 600;">ATS Score: ${item.after_score || '--'}%</span>
                            <span>${new Date(item.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                        </div>
                    </li>
                `).join('');
                
                const listItems = historyList.querySelectorAll('.history-item');
                listItems.forEach((li, index) => {
                    li.addEventListener('click', () => {
                        loadHistoryItem(history[index]);
                    });
                });
            }
            
            historyContainer.classList.remove("hidden");
        } catch (err) {
            showToast("Failed to load version history.", "error", "Fetch Error");
        } finally {
            historyBtn.disabled = false;
            historyBtn.innerHTML = `<span class="btn-text">Version History</span>`;
        }
    });

    function loadHistoryItem(data) {
        currentTailoredId = data.id;
        rawTailoredMarkdown = data.tailored_text;
        
        emptyState?.classList.add("hidden");
        shimmerLoader?.classList.add("hidden");
        matchAnalysisCard?.classList.add("hidden");
        
        if (data.before_score !== null && beforeScoreValue) {
            beforeScoreValue.textContent = `${data.before_score}%`;
        }
        if (data.after_score !== null && afterScoreValue) {
            animateScoreCount(afterScoreValue, data.after_score);
        }
        if (scoresWidget) scoresWidget.classList.remove("hidden");
        
        if (data.analysis_note && analysisNoteText) {
            analysisNoteText.textContent = data.analysis_note;
            analysisNoteCard?.classList.remove("hidden");
        } else {
            analysisNoteCard?.classList.add("hidden");
        }

        if (renderedDocumentOutput) {
            renderedDocumentOutput.innerHTML = renderMarkdownToHTML(rawTailoredMarkdown);
        }

        tabTailorBtn?.click();
        paperContent?.classList.remove("hidden");

        if (downloadPdfBtn) downloadPdfBtn.disabled = false;
        if (downloadDocxBtn) downloadDocxBtn.disabled = false;
        if (copyBtn) copyBtn.disabled = false;
        
        showToast("Loaded tailored resume version.", "success", "History Loaded");
    }

    // Handle Upload Base Resume (Checks auth on submit)
    uploadForm?.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!isAuthenticated) {
            return showCustomAuthModal("Sign In Required", "Please sign in to upload base resumes.");
        }
        if (!fileInput || !fileInput.files.length) return showToast("Please select a file first.", "error", "No File Selected");

        if (uploadBtn) {
            uploadBtn.disabled = true;
            uploadBtn.textContent = "Processing & Extracting...";
        }

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        try {
            const res = await apiFetch("/api/v1/resume/upload", {
                method: "POST",
                body: formData
            });

            if (!res.ok) {
                if (res.status === 401) {
                    isAuthenticated = false;
                    showCustomAuthModal("Session Expired", "Your session has expired. Please sign in to upload resumes.");
                    throw new Error("Session expired. Please sign in again.");
                }
                const err = await res.json();
                throw new Error(err.detail || "Upload failed");
            }

            const data = await res.json();
            showToast("Base resume uploaded and extracted successfully.", "success", "Upload Complete");
            displayActiveResume(data.filename);
        } catch (err) {
            showCustomAlert("Upload Error", err.message, "error");
        } finally {
            if (uploadBtn) {
                uploadBtn.disabled = false;
                uploadBtn.textContent = "Upload & Extract Resume";
            }
        }
    });

    // Handle Delete Active Base Resume (Checks auth on click)
    deleteResumeBtn?.addEventListener("click", async () => {
        if (!isAuthenticated) {
            return showCustomAuthModal("Sign In Required", "Please sign in to manage base resumes.");
        }
        
        const confirmed = await showCustomConfirm(
            "Delete Base Resume?",
            "Are you sure you want to delete your active master resume? This action cannot be undone."
        );
        if (!confirmed) return;
        
        try {
            const res = await apiFetch("/api/v1/resume/active", {
                method: "DELETE"
            });
            
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Failed to delete resume");
            }
            
            activeResumeBadge?.classList.add("hidden");
            if (fileNameDisplay) fileNameDisplay.textContent = "Drag & Drop Resume or Browse";
            if (fileInput) fileInput.value = "";
            showToast("Base resume deleted successfully.", "success", "Deleted");
            
        } catch (err) {
            showCustomAlert("Delete Error", err.message, "error");
        }
    });

    // FEATURE 1: HANDLE MATCH ANALYZER REQUEST (Checks auth on click)
    submitMatchBtn?.addEventListener("click", async () => {
        if (!isAuthenticated) {
            return showCustomAuthModal("Sign In Required", "Please sign in to run Match Score Analysis.");
        }
        
        const jobTitle = document.getElementById("jobTitleInput")?.value || "Target Position";
        const jobDescription = document.getElementById("jdInput")?.value || "";

        if (!jobDescription.trim()) {
            return showToast("Please enter a target job description.", "error", "Missing Description");
        }

        emptyState?.classList.add("hidden");
        paperContent?.classList.add("hidden");
        matchAnalysisCard?.classList.add("hidden");
        shimmerLoader?.classList.remove("hidden");

        submitMatchBtn.disabled = true;
        submitMatchBtn.innerHTML = `<span>Analyzing Match with Groq...</span>`;

        try {
            const res = await apiFetch("/api/v1/tailor/analyze-match", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    job_title: jobTitle,
                    job_description: jobDescription
                })
            });

            if (!res.ok) {
                if (res.status === 401) {
                    isAuthenticated = false;
                    showCustomAuthModal("Session Expired", "Your session has expired. Please sign in to analyze match scores.");
                    throw new Error("Session expired. Please sign in again.");
                }
                const err = await res.json();
                throw new Error(err.detail || "Match analysis failed");
            }

            const data = await res.json();
            currentAnalysisData = data;

            renderMatchAnalysisCard(data);

            shimmerLoader?.classList.add("hidden");
            tabMatchBtn?.click();
            matchAnalysisCard?.classList.remove("hidden");

            showToast(`Match score computed: ${data.match_score}%`, "success", "Analysis Complete");
            fetchUsageStatus();
        } catch (err) {
            shimmerLoader?.classList.add("hidden");
            emptyState?.classList.remove("hidden");
            showCustomAlert("Match Analysis Limit / Error", err.message, "error");
            fetchUsageStatus();
        } finally {
            submitMatchBtn.disabled = false;
            submitMatchBtn.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                <span>Analyze Match Score</span>`;
        }
    });

    function renderMatchAnalysisCard(data) {
        if (matchGaugeValue) matchGaugeValue.textContent = `${data.match_score}%`;
        if (keywordsText) keywordsText.textContent = `${data.keywords_found} / ${data.keywords_total} Keywords Found`;
        if (matchProgressBar) matchProgressBar.style.width = `${data.match_score}%`;

        // Render Matched Skills Badges
        if (skillsMatchedContainer) {
            skillsMatchedContainer.innerHTML = (data.skills_matched || []).map(skill => 
                `<span class="skill-badge matched">${skill}</span>`
            ).join('');
        }

        // Render Missing Skills Badges
        if (skillsMissingContainer) {
            skillsMissingContainer.innerHTML = (data.skills_missing || []).map(skill => 
                `<span class="skill-badge missing">${skill}</span>`
            ).join('');
        }

        // Render Recommendations List
        if (recommendationsList) {
            recommendationsList.innerHTML = (data.recommendations || []).map(rec => 
                `<li>${rec}</li>`
            ).join('');
        }
    }

    // FEATURE 2: HANDLE TAILOR REQUEST (Checks auth on submit)
    tailorForm?.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (activeFeatureMode === "match") return; // SubmitMatchBtn handles match analysis
        
        if (!isAuthenticated) {
            return showCustomAuthModal("Sign In Required", "Please sign in to align and tailor your resume.");
        }
        
        const jobTitle = document.getElementById("jobTitleInput")?.value || "";
        const jobDescription = document.getElementById("jdInput")?.value || "";
        
        emptyState?.classList.add("hidden");
        paperContent?.classList.add("hidden");
        matchAnalysisCard?.classList.add("hidden");
        shimmerLoader?.classList.remove("hidden");
        scoresWidget?.classList.add("hidden");
        analysisNoteCard?.classList.add("hidden");

        if (submitTailorBtn) {
            submitTailorBtn.disabled = true;
            submitTailorBtn.innerHTML = `<span>Aligning Resume with Groq...</span>`;
        }

        try {
            const res = await apiFetch("/api/v1/tailor/align", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    job_title: jobTitle,
                    job_description: jobDescription,
                    linkedin_url: document.getElementById("linkedinInput")?.value || "",
                    github_url: document.getElementById("githubInput")?.value || "",
                    portfolio_url: document.getElementById("portfolioInput")?.value || null
                })
            });

            if (!res.ok) {
                if (res.status === 401) {
                    isAuthenticated = false;
                    showCustomAuthModal("Session Expired", "Your session has expired. Please sign in to tailor your resume.");
                    throw new Error("Session expired. Please sign in again.");
                }
                const err = await res.json();
                throw new Error(err.detail || "Tailoring failed");
            }

            const data = await res.json();
            currentTailoredId = data.id;
            rawTailoredMarkdown = data.tailored_text;

            if (data.before_score !== null && beforeScoreValue) {
                beforeScoreValue.textContent = `${data.before_score}%`;
            }
            if (data.after_score !== null && afterScoreValue) {
                animateScoreCount(afterScoreValue, data.after_score);
            }
            if (scoresWidget) scoresWidget.classList.remove("hidden");
            
            if (data.analysis_note && analysisNoteText) {
                analysisNoteText.textContent = data.analysis_note;
                analysisNoteCard?.classList.remove("hidden");
            } else {
                analysisNoteCard?.classList.add("hidden");
            }

            if (renderedDocumentOutput) {
                renderedDocumentOutput.innerHTML = renderMarkdownToHTML(rawTailoredMarkdown);
            }

            shimmerLoader?.classList.add("hidden");
            tabTailorBtn?.click();
            paperContent?.classList.remove("hidden");

            if (downloadPdfBtn) downloadPdfBtn.disabled = false;
            if (downloadDocxBtn) downloadDocxBtn.disabled = false;
            if (copyBtn) copyBtn.disabled = false;

            showToast("Resume tailored successfully.", "success", "Alignment Complete");
            fetchUsageStatus();
        } catch (err) {
            shimmerLoader?.classList.add("hidden");
            emptyState?.classList.remove("hidden");
            showCustomAlert("Resume Tailor Limit / Error", err.message, "error");
            fetchUsageStatus();
        } finally {
            if (submitTailorBtn) {
                submitTailorBtn.disabled = false;
                submitTailorBtn.innerHTML = `
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
                    <span>Tailor Resume with AI</span>`;
            }
        }
    });

    // Download PDF Action (Checks auth on click)
    downloadPdfBtn?.addEventListener("click", () => {
        if (!isAuthenticated) return showCustomAuthModal("Sign In Required", "Please sign in to download resumes.");
        if (!currentTailoredId) return showToast("No tailored resume ready for download.", "error", "Not Ready");
        window.location.href = `${API_BASE}/api/v1/tailor/download-pdf/${currentTailoredId}`;
        showToast("Generating PDF document...", "info", "Downloading PDF");
    });

    // Download Word Action (Checks auth on click)
    downloadDocxBtn?.addEventListener("click", () => {
        if (!isAuthenticated) return showCustomAuthModal("Sign In Required", "Please sign in to download resumes.");
        if (!currentTailoredId) return showToast("No tailored resume ready for download.", "error", "Not Ready");
        window.location.href = `${API_BASE}/api/v1/tailor/download-docx/${currentTailoredId}`;
        showToast("Generating Word document...", "info", "Downloading DOCX");
    });

    // Copy to Clipboard Action
    copyBtn?.addEventListener("click", () => {
        if (!rawTailoredMarkdown) return;
        navigator.clipboard.writeText(rawTailoredMarkdown);
        showToast("Tailored resume copied to clipboard.", "success", "Copied");
    });

    async function fetchActiveResume() {
        try {
            const res = await apiFetch("/api/v1/resume/active");
            if (res.ok) {
                const data = await res.json();
                displayActiveResume(data.filename);
            }
        } catch (_) {}
    }

    function displayActiveResume(filename) {
        if (activeResumeName) activeResumeName.textContent = filename;
        activeResumeBadge?.classList.remove("hidden");
    }

    // Micro-animation for ATS score counter
    function animateScoreCount(element, targetScore) {
        let current = 0;
        const duration = 1000;
        const stepTime = 20;
        const steps = duration / stepTime;
        const increment = targetScore / steps;

        const timer = setInterval(() => {
            current += increment;
            if (current >= targetScore) {
                element.textContent = `${targetScore}%`;
                clearInterval(timer);
            } else {
                element.textContent = `${Math.floor(current)}%`;
            }
        }, stepTime);
    }

    // Markdown to HTML renderer with professional badges
    function renderMarkdownToHTML(markdown) {
        if (!markdown) return "";
        let html = markdown
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^### (.*$)/gim, '### $1')
            .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/gim, 'em>$1</em>')
            .replace(/\[LinkedIn\]\((.*?)\)/gim, '<a href="$1" target="_blank" class="social-link-badge">LinkedIn</a>')
            .replace(/\[GitHub\]\((.*?)\)/gim, '<a href="$1" target="_blank" class="social-link-badge">GitHub</a>')
            .replace(/\[Portfolio\]\((.*?)\)/gim, '<a href="$1" target="_blank" class="social-link-badge">Portfolio</a>')
            .replace(/\[(.*?)\]\((.*?)\)/gim, '<a href="$2" target="_blank" style="color: #0284c7; text-decoration: underline;">$1</a>')
            .replace(/^\- (.*$)/gim, '<ul><li>$1</li></ul>')
            .replace(/<\/ul>\s*<ul>/gim, '');

        return html.split('\n\n').map(p => {
            if (p.trim().startsWith('<h') || p.trim().startsWith('<ul')) return p;
            
            if (p.includes('|') || p.includes('LinkedIn') || p.includes('GitHub')) {
                return `<p style="text-align: center; margin-top: 0; color: #475569; font-size: 0.9rem;">${p.replace(/\n/g, '<br>')}</p>`;
            }
            return `<p>${p.replace(/\n/g, '<br>')}</p>`;
        }).join('');
    }

    // Floating Bubble Toast System
    function showToast(message, type = "info", title = "") {
        if (!toastContainer) return showCustomAlert(title || "Notification", message, type);

        const toast = document.createElement("div");
        toast.className = `toast-bubble toast-${type}`;
        
        let iconSvg = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;

        if (type === "success") {
            iconSvg = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
        } else if (type === "error") {
            iconSvg = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`;
        }

        toast.innerHTML = `
            <div class="toast-bubble-icon">${iconSvg}</div>
            <div class="toast-bubble-content">
                <span class="toast-bubble-title">${title || 'Notification'}</span>
                <span class="toast-bubble-msg">${message}</span>
            </div>
        `;

        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.classList.add("fade-out");
            setTimeout(() => toast.remove(), 350);
        }, 4000);
    }
});

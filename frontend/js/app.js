document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const uploadForm = document.getElementById("uploadForm");
    const fileInput = document.getElementById("resumeFileInput");
    const fileNameDisplay = document.getElementById("fileNameDisplay");
    const activeResumeBadge = document.getElementById("activeResumeBadge");
    const activeResumeName = document.getElementById("activeResumeName");
    const deleteResumeBtn = document.getElementById("deleteResumeBtn");
    const uploadBtn = document.getElementById("uploadBtn");
    
    const tailorForm = document.getElementById("tailorForm");
    const submitTailorBtn = document.getElementById("submitTailorBtn");
    const historyBtn = document.getElementById("historyBtn");
    const historyContainer = document.getElementById("historyContainer");
    const historyList = document.getElementById("historyList");
    const temperatureRange = document.getElementById("temperatureRange");
    const tempValue = document.getElementById("tempValue");

    const emptyState = document.getElementById("emptyState");
    const shimmerLoader = document.getElementById("shimmerLoader");
    const paperContent = document.getElementById("paperContent");
    const renderedDocumentOutput = document.getElementById("renderedDocumentOutput");
    
    const scoresWidget = document.getElementById("scoresWidget");
    const beforeScoreValue = document.getElementById("beforeScoreValue");
    const afterScoreValue = document.getElementById("afterScoreValue");
    const analysisNoteCard = document.getElementById("analysisNoteCard");
    const analysisNoteText = document.getElementById("analysisNoteText");
    
    const downloadPdfBtn = document.getElementById("downloadPdfBtn");
    const downloadDocxBtn = document.getElementById("downloadDocxBtn");
    const copyBtn = document.getElementById("copyBtn");
    const toastContainer = document.getElementById("toastContainer");

    // Auth Elements
    const loginBtn = document.getElementById("loginBtn");
    const logoutBtn = document.getElementById("logoutBtn");
    const userProfile = document.getElementById("userProfile");
    const userAvatar = document.getElementById("userAvatar");
    const userName = document.getElementById("userName");

    let currentTailoredId = null;
    let rawTailoredMarkdown = "";
    let isAuthenticated = false;
    
    // Caching state to prevent duplicate requests
    let lastSubmittedJobTitle = "";
    let lastSubmittedJobDesc = "";

    // Check Auth Status on Load
    checkAuthStatus();

    async function checkAuthStatus() {
        try {
            const res = await fetch("/api/v1/auth/me");
            if (res.ok) {
                const user = await res.json();
                isAuthenticated = true;
                loginBtn?.classList.add("hidden");
                userProfile?.classList.remove("hidden");
                if (userName) userName.textContent = user.name || user.email;
                if (userAvatar && user.picture) userAvatar.src = user.picture;
                
                fetchActiveResume();
            } else {
                isAuthenticated = false;
                loginBtn?.classList.remove("hidden");
                userProfile?.classList.add("hidden");
                
                if (emptyState) {
                    emptyState.innerHTML = `
                        <div class="empty-icon-bubble">🔒</div>
                        <h3>Authentication Required</h3>
                        <p>Please <strong>Sign in with Google</strong> using the header button to upload resumes and unlock the AI Alignment Studio.</p>`;
                }
            }
        } catch (err) {
            console.error("Auth check failed:", err);
        }
    }

    loginBtn?.addEventListener("click", () => {
        window.location.href = "/api/v1/auth/login";
    });

    logoutBtn?.addEventListener("click", async () => {
        try {
            await fetch("/api/v1/auth/logout", { method: "POST" });
            showToast("Logged out successfully", "success", "Goodbye!");
            setTimeout(() => window.location.reload(), 1000);
        } catch (err) {
            showToast("Logout failed", "error");
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
            showToast(`Selected file: ${e.target.files[0].name}`, "info", "File Selected");
        }
    });

    // Version History Logic
    historyBtn?.addEventListener("click", async () => {
        if (!isAuthenticated) return showToast("Please sign in to view history.", "error", "Access Denied");
        
        if (!historyContainer.classList.contains("hidden")) {
            historyContainer.classList.add("hidden");
            return;
        }

        historyBtn.disabled = true;
        historyBtn.textContent = "Loading...";

        try {
            const res = await fetch("/api/v1/tailor/history");
            if (!res.ok) throw new Error("Failed to fetch history");
            
            const history = await res.json();
            
            if (history.length === 0) {
                historyList.innerHTML = `<li style="font-size: 0.82rem; color: var(--text-muted); text-align: center; padding: 0.5rem;">No history found in the last 6 hours.</li>`;
            } else {
                historyList.innerHTML = history.map(item => `
                    <li class="history-item" data-id="${item.id}" style="padding: 0.65rem 0.85rem; background: var(--glass-card); border: 1px solid var(--glass-border); border-radius: var(--radius-bubble-sm); cursor: pointer; transition: all 0.25s ease;">
                        <div style="font-size: 0.85rem; font-weight: 700; color: var(--text-main);">${item.job_title || 'Target Role'}</div>
                        <div style="font-size: 0.75rem; color: var(--text-muted); display: flex; justify-content: space-between; margin-top: 0.35rem;">
                            <span style="color: var(--accent-emerald); font-weight: 600;">Match Score: ${item.after_score || '--'}%</span>
                            <span>${new Date(item.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                        </div>
                    </li>
                `).join('');
                
                const listItems = historyList.querySelectorAll('.history-item');
                listItems.forEach((li, index) => {
                    li.addEventListener('click', () => {
                        loadHistoryItem(history[index]);
                    });
                    li.addEventListener('mouseenter', () => {
                        li.style.borderColor = 'var(--accent-indigo)';
                        li.style.transform = 'translateX(4px)';
                    });
                    li.addEventListener('mouseleave', () => {
                        li.style.borderColor = 'var(--glass-border)';
                        li.style.transform = 'translateX(0)';
                    });
                });
            }
            
            historyContainer.classList.remove("hidden");
        } catch (err) {
            showToast("Failed to load version history.", "error", "Fetch Error");
        } finally {
            historyBtn.disabled = false;
            historyBtn.innerHTML = `<span class="btn-icon">🕒</span><span class="btn-text">Version History</span>`;
        }
    });

    function loadHistoryItem(data) {
        currentTailoredId = data.id;
        rawTailoredMarkdown = data.tailored_text;
        
        emptyState?.classList.add("hidden");
        shimmerLoader?.classList.add("hidden");
        
        // Render Scores with micro-animation
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

        paperContent?.classList.remove("hidden");

        if (downloadPdfBtn) downloadPdfBtn.disabled = false;
        if (downloadDocxBtn) downloadDocxBtn.disabled = false;
        if (copyBtn) copyBtn.disabled = false;
        
        showToast("Loaded tailored resume version.", "success", "History Loaded");
    }

    // Handle Upload Base Resume
    uploadForm?.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!isAuthenticated) return showToast("Please sign in to upload resumes.", "error", "Auth Required");
        if (!fileInput || !fileInput.files.length) return showToast("Please select a file first.", "error", "No File");

        if (uploadBtn) {
            uploadBtn.disabled = true;
            uploadBtn.textContent = "Processing & Extracting...";
        }

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        try {
            const res = await fetch("/api/v1/resume/upload", {
                method: "POST",
                body: formData
            });

            if (!res.ok) {
                if (res.status === 401) throw new Error("Session expired. Please sign in again.");
                const err = await res.json();
                throw new Error(err.detail || "Upload failed");
            }

            const data = await res.json();
            showToast("Base resume uploaded and extracted successfully!", "success", "Upload Complete");
            displayActiveResume(data.filename);
        } catch (err) {
            showToast(err.message, "error", "Upload Failed");
        } finally {
            if (uploadBtn) {
                uploadBtn.disabled = false;
                uploadBtn.textContent = "Upload & Extract Resume";
            }
        }
    });

    // Handle Delete Active Base Resume
    deleteResumeBtn?.addEventListener("click", async () => {
        if (!isAuthenticated) return showToast("Please sign in first.", "error", "Auth Required");
        if (!confirm("Are you sure you want to delete your active base resume?")) return;
        
        try {
            const res = await fetch("/api/v1/resume/active", {
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
            
            if (historyList) historyList.innerHTML = `<li style="font-size: 0.82rem; color: var(--text-muted); text-align: center; padding: 0.5rem;">No history found.</li>`;
            
        } catch (err) {
            showToast(err.message, "error", "Delete Error");
        }
    });

    // Handle Tailor Request
    tailorForm?.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!isAuthenticated) return showToast("Please sign in to align your resume.", "error", "Auth Required");
        
        const jobTitle = document.getElementById("jobTitleInput")?.value || "";
        const jobDescription = document.getElementById("jdInput")?.value || "";
        
        if (jobTitle === lastSubmittedJobTitle && jobDescription === lastSubmittedJobDesc) {
            return showToast("You have already tailored a resume for this job description!", "info", "Already Generated");
        }

        emptyState?.classList.add("hidden");
        paperContent?.classList.add("hidden");
        shimmerLoader?.classList.remove("hidden");
        scoresWidget?.classList.add("hidden");
        analysisNoteCard?.classList.add("hidden");

        if (submitTailorBtn) {
            submitTailorBtn.disabled = true;
            submitTailorBtn.innerHTML = `<span class="btn-icon">⚡</span><span>Aligning Resume with AI...</span>`;
        }

        try {
            const res = await fetch("/api/v1/tailor/align", {
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
                if (res.status === 401) throw new Error("Session expired. Please sign in again.");
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
            paperContent?.classList.remove("hidden");

            if (downloadPdfBtn) downloadPdfBtn.disabled = false;
            if (downloadDocxBtn) downloadDocxBtn.disabled = false;
            if (copyBtn) copyBtn.disabled = false;

            lastSubmittedJobTitle = jobTitle;
            lastSubmittedJobDesc = jobDescription;

            showToast("Resume tailored successfully with AI!", "success", "Alignment Complete");
        } catch (err) {
            shimmerLoader?.classList.add("hidden");
            emptyState?.classList.remove("hidden");
            showToast(err.message, "error", "Alignment Failed");
        } finally {
            if (submitTailorBtn) {
                submitTailorBtn.disabled = false;
                submitTailorBtn.innerHTML = `<span class="btn-icon">⚡</span><span>Tailor Resume with AI</span>`;
            }
        }
    });

    // Download PDF Action
    downloadPdfBtn?.addEventListener("click", () => {
        if (!isAuthenticated) return showToast("Please sign in to download.", "error", "Auth Required");
        if (!currentTailoredId) return showToast("No tailored resume ready for download.", "error", "Not Ready");
        window.location.href = `/api/v1/tailor/download-pdf/${currentTailoredId}`;
        showToast("Generating ATS-compliant PDF document...", "success", "Downloading PDF");
    });

    // Download Word Action
    downloadDocxBtn?.addEventListener("click", () => {
        if (!isAuthenticated) return showToast("Please sign in to download.", "error", "Auth Required");
        if (!currentTailoredId) return showToast("No tailored resume ready for download.", "error", "Not Ready");
        window.location.href = `/api/v1/tailor/download-docx/${currentTailoredId}`;
        showToast("Generating editable Word document...", "success", "Downloading DOCX");
    });

    // Copy to Clipboard Action
    copyBtn?.addEventListener("click", () => {
        if (!rawTailoredMarkdown) return;
        navigator.clipboard.writeText(rawTailoredMarkdown);
        showToast("Tailored resume copied to clipboard!", "success", "Copied!");
    });

    async function fetchActiveResume() {
        try {
            const res = await fetch("/api/v1/resume/active");
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
        const duration = 1200; // ms
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

    // Markdown to HTML renderer with interactive social link icons
    function renderMarkdownToHTML(markdown) {
        if (!markdown) return "";
        let html = markdown
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^### (.*$)/gim, '### $1')
            .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/gim, '<em>$1</em>')
            .replace(/\[LinkedIn\]\((.*?)\)/gim, '<a href="$1" target="_blank" class="social-link-badge">💼 LinkedIn</a>')
            .replace(/\[GitHub\]\((.*?)\)/gim, '<a href="$1" target="_blank" class="social-link-badge">🐙 GitHub</a>')
            .replace(/\[Portfolio\]\((.*?)\)/gim, '<a href="$1" target="_blank" class="social-link-badge">🌐 Portfolio</a>')
            .replace(/\[(.*?)\]\((.*?)\)/gim, '<a href="$2" target="_blank" style="color: #2563eb; text-decoration: underline;">$1</a>')
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
        if (!toastContainer) return alert(message);

        const toast = document.createElement("div");
        toast.className = `toast-bubble toast-${type}`;
        
        let icon = "ℹ️";
        let defaultTitle = "Notice";

        if (type === "success") {
            icon = "✓";
            defaultTitle = "Success";
        } else if (type === "error") {
            icon = "✕";
            defaultTitle = "Error";
        }

        toast.innerHTML = `
            <div class="toast-bubble-icon">${icon}</div>
            <div class="toast-bubble-content">
                <span class="toast-bubble-title">${title || defaultTitle}</span>
                <span class="toast-bubble-msg">${message}</span>
            </div>
        `;

        toastContainer.appendChild(toast);

        // Graceful slide-in & auto-dismiss with fade-out animation
        setTimeout(() => {
            toast.classList.add("fade-out");
            setTimeout(() => toast.remove(), 400);
        }, 4000);
    }
});

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const uploadForm = document.getElementById("uploadForm");
    const fileInput = document.getElementById("resumeFileInput");
    const fileNameDisplay = document.getElementById("fileNameDisplay");
    const activeResumeBadge = document.getElementById("activeResumeBadge");
    const activeResumeName = document.getElementById("activeResumeName");
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
                
                // Only fetch active resume if authenticated
                fetchActiveResume();
            } else {
                isAuthenticated = false;
                loginBtn?.classList.remove("hidden");
                userProfile?.classList.add("hidden");
                
                // Show prompt in empty state
                if (emptyState) {
                    emptyState.innerHTML = `<div class="empty-icon">🔒</div>
                                            <h3>Authentication Required</h3>
                                            <p>Please <strong>Sign in with Google</strong> using the button in the top right to upload resumes and use the AI Tailoring Studio.</p>`;
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
            window.location.reload();
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

    // Fetch Active Base Resume is now called inside checkAuthStatus()

    // File Input Display
    fileInput?.addEventListener("change", (e) => {
        if (e.target.files.length > 0 && fileNameDisplay) {
            fileNameDisplay.textContent = e.target.files[0].name;
        }
    });

    // Version History Logic
    historyBtn?.addEventListener("click", async () => {
        if (!isAuthenticated) return showToast("Please sign in to view history.", "error");
        
        // Toggle visibility
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
                historyList.innerHTML = `<li style="font-size: 0.85rem; color: #94a3b8; text-align: center;">No history found in the last 6 hours.</li>`;
            } else {
                historyList.innerHTML = history.map(item => `
                    <li class="history-item" data-id="${item.id}" style="padding: 0.5rem; background: #fff; border: 1px solid #e2e8f0; border-radius: 4px; cursor: pointer; transition: all 0.2s;">
                        <div style="font-size: 0.85rem; font-weight: 600; color: #1e293b;">${item.job_title || 'Target Role'}</div>
                        <div style="font-size: 0.75rem; color: #64748b; display: flex; justify-content: space-between; margin-top: 0.25rem;">
                            <span>Score: ${item.after_score || '--'}%</span>
                            <span>${new Date(item.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                        </div>
                    </li>
                `).join('');
                
                // Add click events to load history items
                const listItems = historyList.querySelectorAll('.history-item');
                listItems.forEach((li, index) => {
                    li.addEventListener('click', () => {
                        loadHistoryItem(history[index]);
                    });
                    li.addEventListener('mouseenter', () => li.style.borderColor = '#3b82f6');
                    li.addEventListener('mouseleave', () => li.style.borderColor = '#e2e8f0');
                });
            }
            
            historyContainer.classList.remove("hidden");
        } catch (err) {
            showToast("Failed to load history.", "error");
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
        
        // Render Scores and Notes
        if (data.before_score !== null && beforeScoreValue) {
            beforeScoreValue.textContent = `${data.before_score}%`;
        }
        if (data.after_score !== null && afterScoreValue) {
            afterScoreValue.textContent = `${data.after_score}%`;
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
        
        showToast("Loaded tailored resume from history.", "success");
    }

    // Handle Upload Base Resume
    uploadForm?.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!isAuthenticated) return showToast("Please sign in to upload resumes.", "error");
        if (!fileInput || !fileInput.files.length) return showToast("Please select a file to upload.", "error");

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
                if (res.status === 401) {
                    throw new Error("Session expired. Please sign in again.");
                }
                const err = await res.json();
                throw new Error(err.detail || "Upload failed");
            }

            const data = await res.json();
            showToast("Base resume uploaded and extracted successfully!", "success");
            displayActiveResume(data.filename);
        } catch (err) {
            showToast("Upload Error: " + err.message, "error");
        } finally {
            if (uploadBtn) {
                uploadBtn.disabled = false;
                uploadBtn.textContent = "Upload & Extract Resume";
            }
        }
    });

    // Handle Tailor Request
    tailorForm?.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!isAuthenticated) return showToast("Please sign in to align your resume.", "error");
        
        const jobTitle = document.getElementById("jobTitleInput")?.value || "";
        const jobDescription = document.getElementById("jdInput")?.value || "";
        
        // Prevent duplicate submissions for the exact same job description
        if (jobTitle === lastSubmittedJobTitle && jobDescription === lastSubmittedJobDesc) {
            return showToast("You have already tailored a resume for this exact job description! The result is currently displayed.", "info");
        }

        // Show Shimmer Skeleton Loading State
        emptyState?.classList.add("hidden");
        paperContent?.classList.add("hidden");
        shimmerLoader?.classList.remove("hidden");
        scoresWidget?.classList.add("hidden");
        analysisNoteCard?.classList.add("hidden");

        if (submitTailorBtn) {
            submitTailorBtn.disabled = true;
            submitTailorBtn.innerHTML = `<span class="btn-icon">⏳</span><span>Aligning Resume with AI...</span>`;
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
                if (res.status === 401) {
                    throw new Error("Session expired. Please sign in again.");
                }
                const err = await res.json();
                throw new Error(err.detail || "Tailoring failed");
            }

            const data = await res.json();
            currentTailoredId = data.id;
            rawTailoredMarkdown = data.tailored_text;

            // Render Scores and Notes
            if (data.before_score !== null && beforeScoreValue) {
                beforeScoreValue.textContent = `${data.before_score}%`;
            }
            if (data.after_score !== null && afterScoreValue) {
                afterScoreValue.textContent = `${data.after_score}%`;
            }
            if (scoresWidget) scoresWidget.classList.remove("hidden");
            
            if (data.analysis_note && analysisNoteText) {
                analysisNoteText.textContent = data.analysis_note;
                analysisNoteCard?.classList.remove("hidden");
            } else {
                analysisNoteCard?.classList.add("hidden");
            }

            // Render Markdown Document inside Paper Viewport
            if (renderedDocumentOutput) {
                renderedDocumentOutput.innerHTML = renderMarkdownToHTML(rawTailoredMarkdown);
            }

            // Hide Loader, Show Paper
            shimmerLoader?.classList.add("hidden");
            paperContent?.classList.remove("hidden");

            // Enable Actions
            if (downloadPdfBtn) downloadPdfBtn.disabled = false;
            if (downloadDocxBtn) downloadDocxBtn.disabled = false;
            if (copyBtn) copyBtn.disabled = false;

            // Update caching state
            lastSubmittedJobTitle = jobTitle;
            lastSubmittedJobDesc = jobDescription;

            showToast("Resume tailored successfully!", "success");
        } catch (err) {
            shimmerLoader?.classList.add("hidden");
            emptyState?.classList.remove("hidden");
            showToast("Tailor Error: " + err.message, "error");
        } finally {
            if (submitTailorBtn) {
                submitTailorBtn.disabled = false;
                submitTailorBtn.innerHTML = `<span class="btn-icon">⚡</span><span>Tailor Resume with AI</span>`;
            }
        }
    });

    // Download PDF Action
    downloadPdfBtn?.addEventListener("click", () => {
        if (!isAuthenticated) return showToast("Please sign in to download.", "error");
        if (!currentTailoredId) return showToast("No tailored resume ready for download.", "error");
        window.location.href = `/api/v1/tailor/download-pdf/${currentTailoredId}`;
        showToast("Generating ATS PDF download...", "info");
    });

    // Download Word Action
    downloadDocxBtn?.addEventListener("click", () => {
        if (!isAuthenticated) return showToast("Please sign in to download.", "error");
        if (!currentTailoredId) return showToast("No tailored resume ready for download.", "error");
        window.location.href = `/api/v1/tailor/download-docx/${currentTailoredId}`;
        showToast("Generating ATS Word document...", "info");
    });

    // Copy to Clipboard Action
    copyBtn?.addEventListener("click", () => {
        if (!rawTailoredMarkdown) return;
        navigator.clipboard.writeText(rawTailoredMarkdown);
        showToast("Tailored resume copied to clipboard!", "success");
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

    // Pure Markdown to HTML parser for Document Paper Viewport
    function renderMarkdownToHTML(markdown) {
        if (!markdown) return "";
        let html = markdown
            .replace(/^# (.*$)/gim, '<h1 style="text-align: center; margin-bottom: 0.2rem; color: #1e293b;">$1</h1>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^### (.*$)/gim, '### $1')
            .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/gim, '<em>$1</em>')
            .replace(/\[(.*?)\]\((.*?)\)/gim, '<a href="$2" target="_blank" style="color: #3b82f6; text-decoration: none;">$1</a>')
            .replace(/^\- (.*$)/gim, '<ul><li>$1</li></ul>')
            .replace(/<\/ul>\s*<ul>/gim, ''); // Merge consecutive ul blocks
            
        // Wrap plain text lines in <p>
        return html.split('\n\n').map(p => {
            if (p.trim().startsWith('<h') || p.trim().startsWith('<ul')) return p;
            
            // Center align contact info line
            if (p.includes('|') && p.includes('@')) {
                return `<p style="text-align: center; margin-top: 0; color: #475569; font-size: 0.9rem;">${p.replace(/\n/g, '<br>')}</p>`;
            }
            return `<p>${p.replace(/\n/g, '<br>')}</p>`;
        }).join('');
    }

    function showToast(message, type = "info") {
        if (!toastContainer) return alert(message);
        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toastContainer.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }
});

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
    const temperatureRange = document.getElementById("temperatureRange");
    const tempValue = document.getElementById("tempValue");

    const emptyState = document.getElementById("emptyState");
    const shimmerLoader = document.getElementById("shimmerLoader");
    const paperContent = document.getElementById("paperContent");
    const renderedDocumentOutput = document.getElementById("renderedDocumentOutput");
    
    const matchScoreWidget = document.getElementById("matchScoreWidget");
    const matchScoreValue = document.getElementById("matchScoreValue");
    
    const downloadPdfBtn = document.getElementById("downloadPdfBtn");
    const downloadDocxBtn = document.getElementById("downloadDocxBtn");
    const copyBtn = document.getElementById("copyBtn");
    const toastContainer = document.getElementById("toastContainer");

    let currentTailoredId = null;
    let rawTailoredMarkdown = "";

    // Temperature slider update
    if (temperatureRange && tempValue) {
        temperatureRange.addEventListener("input", (e) => {
            tempValue.textContent = e.target.value;
        });
    }

    // Fetch Active Base Resume on Load
    fetchActiveResume();

    // File Input Display
    fileInput?.addEventListener("change", (e) => {
        if (e.target.files.length > 0 && fileNameDisplay) {
            fileNameDisplay.textContent = e.target.files[0].name;
        }
    });

    // Handle Upload Base Resume
    uploadForm?.addEventListener("submit", async (e) => {
        e.preventDefault();
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
        const jobTitle = document.getElementById("jobTitleInput")?.value || "";
        const jobDescription = document.getElementById("jdInput")?.value || "";

        // Show Shimmer Skeleton Loading State (defensive optional chaining)
        emptyState?.classList.add("hidden");
        paperContent?.classList.add("hidden");
        shimmerLoader?.classList.remove("hidden");
        matchScoreWidget?.classList.add("hidden");

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
                    job_description: jobDescription
                })
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Tailoring failed");
            }

            const data = await res.json();
            currentTailoredId = data.id;
            rawTailoredMarkdown = data.tailored_text;

            // Calculate ATS Match Score
            const score = calculateATSScore(jobDescription, rawTailoredMarkdown);
            renderATSScore(score);

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
        if (!currentTailoredId) return showToast("No tailored resume ready for download.", "error");
        window.location.href = `/api/v1/tailor/download-pdf/${currentTailoredId}`;
        showToast("Generating ATS PDF download...", "info");
    });

    // Download Word Action
    downloadDocxBtn?.addEventListener("click", () => {
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

    // ATS Match Score Calculator Widget
    function calculateATSScore(jdText, tailoredText) {
        if (!jdText || !tailoredText) return 85;
        const stopwords = new Set(["and", "the", "with", "for", "that", "this", "from", "have", "you", "your", "are", "will", "our"]);
        const extractKeywords = (str) => {
            return (str.toLowerCase().match(/\b[a-z]{3,}\b/g) || [])
                .filter(w => !stopwords.has(w));
        };

        const jdWords = Array.from(new Set(extractKeywords(jdText)));
        const tailoredWords = new Set(extractKeywords(tailoredText));

        if (jdWords.length === 0) return 90;

        let matched = 0;
        jdWords.forEach(word => {
            if (tailoredWords.has(word)) matched++;
        });

        const percentage = Math.round((matched / jdWords.length) * 100);
        return Math.min(Math.max(percentage + 20, 78), 98); // Baseline score range
    }

    function renderATSScore(score) {
        if (matchScoreValue) matchScoreValue.textContent = `${score}%`;
        matchScoreWidget?.classList.remove("hidden");
    }

    // Pure Markdown to HTML parser for Document Paper Viewport
    function renderMarkdownToHTML(markdown) {
        if (!markdown) return "";
        let html = markdown
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^### (.*$)/gim, '### $1')
            .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/gim, '<em>$1</em>')
            .replace(/^\- (.*$)/gim, '<ul><li>$1</li></ul>')
            .replace(/<\/ul>\s*<ul>/gim, ''); // Merge consecutive ul blocks
            
        // Wrap plain text lines in <p>
        return html.split('\n\n').map(p => {
            if (p.trim().startsWith('<h') || p.trim().startsWith('<ul')) return p;
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

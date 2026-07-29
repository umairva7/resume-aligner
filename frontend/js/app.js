document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("uploadForm");
    const fileInput = document.getElementById("resumeFileInput");
    const fileNameDisplay = document.getElementById("fileNameDisplay");
    const activeResumeBadge = document.getElementById("activeResumeBadge");
    const activeResumeName = document.getElementById("activeResumeName");
    
    const tailorForm = document.getElementById("tailorForm");
    const submitTailorBtn = document.getElementById("submitTailorBtn");
    const outputSection = document.getElementById("outputSection");
    const tailoredResultOutput = document.getElementById("tailoredResultOutput");
    const copyBtn = document.getElementById("copyBtn");
    const downloadPdfBtn = document.getElementById("downloadPdfBtn");

    let currentTailoredId = null;

    // Fetch Active Base Resume on Load
    fetchActiveResume();

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            fileNameDisplay.textContent = e.target.files[0].name;
        }
    });

    // Handle Upload Base Resume
    uploadForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!fileInput.files.length) return alert("Please select a file.");

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
            alert("Base resume uploaded successfully!");
            displayActiveResume(data.filename);
        } catch (err) {
            alert("Error: " + err.message);
        }
    });

    // Handle Tailor Request
    tailorForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const jobTitle = document.getElementById("jobTitleInput").value;
        const jobDescription = document.getElementById("jdInput").value;

        submitTailorBtn.disabled = true;
        submitTailorBtn.innerHTML = "⏳ Tailoring Resume with AI (may take 5-10s)...";

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
            outputSection.classList.remove("hidden");
            tailoredResultOutput.textContent = data.tailored_text;
            outputSection.scrollIntoView({ behavior: "smooth" });
        } catch (err) {
            alert("Tailor Error: " + err.message);
        } finally {
            submitTailorBtn.disabled = false;
            submitTailorBtn.innerHTML = "✨ Tailor Resume with AI";
        }
    });

    // Download ATS-Friendly PDF
    downloadPdfBtn.addEventListener("click", () => {
        if (!currentTailoredId) return alert("No tailored resume available to download.");
        window.location.href = `/api/v1/tailor/download-pdf/${currentTailoredId}`;
    });

    // Copy to Clipboard
    copyBtn.addEventListener("click", () => {
        navigator.clipboard.writeText(tailoredResultOutput.textContent);
        copyBtn.textContent = "✅ Copied!";
        setTimeout(() => copyBtn.textContent = "📋 Copy Text", 2000);
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
        activeResumeName.textContent = filename;
        activeResumeBadge.classList.remove("hidden");
    }
});

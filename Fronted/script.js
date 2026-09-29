// =====================================================
// PDF MERGER - FRONTEND JAVASCRIPT
// =====================================================


// =====================================================
// RENDER BACKEND URL
// =====================================================

// For local testing:
// const API_URL = "http://127.0.0.1:8000";

// After deploying backend to Render,
// replace the URL below with your actual Render URL.

const API_URL = "https://pragyanai-python-project-super30.onrender.com";


// =====================================================
// GET HTML ELEMENTS
// =====================================================

const fileInput = document.getElementById("fileInput");
const browseBtn = document.getElementById("browseBtn");
const dropZone = document.getElementById("dropZone");

const fileList = document.getElementById("fileList");
const fileCount = document.getElementById("fileCount");

const clearBtn = document.getElementById("clearBtn");
const mergeBtn = document.getElementById("mergeBtn");

const message = document.getElementById("message");

const downloadSection =
    document.getElementById("downloadSection");

const downloadBtn =
    document.getElementById("downloadBtn");


// =====================================================
// STORE SELECTED FILES
// =====================================================

let files = [];


// =====================================================
// BROWSE BUTTON
// =====================================================

browseBtn.addEventListener("click", function () {

    fileInput.click();

});


// =====================================================
// FILE INPUT CHANGE
// =====================================================

fileInput.addEventListener("change", function (event) {

    addFiles(event.target.files);

    // Allow selecting the same file again later
    fileInput.value = "";

});


// =====================================================
// DRAG OVER
// =====================================================

dropZone.addEventListener("dragover", function (event) {

    event.preventDefault();

    dropZone.classList.add("dragover");

});


// =====================================================
// DRAG LEAVE
// =====================================================

dropZone.addEventListener("dragleave", function () {

    dropZone.classList.remove("dragover");

});


// =====================================================
// DROP FILES
// =====================================================

dropZone.addEventListener("drop", function (event) {

    event.preventDefault();

    dropZone.classList.remove("dragover");

    addFiles(event.dataTransfer.files);

});


// =====================================================
// ADD FILES
// =====================================================

function addFiles(newFiles) {

    let addedFiles = 0;

    for (const file of newFiles) {

        // Check PDF type
        const isPDF =
            file.type === "application/pdf" ||
            file.name.toLowerCase().endsWith(".pdf");

        if (!isPDF) {

            showMessage(
                `❌ ${file.name} is not a PDF file.`,
                "error"
            );

            continue;
        }


        // Check duplicate files
        const duplicate = files.some(
            existingFile =>
                existingFile.name === file.name &&
                existingFile.size === file.size
        );

        if (duplicate) {

            continue;
        }


        files.push(file);

        addedFiles++;
    }


    displayFiles();


    if (addedFiles > 0) {

        showMessage(
            `${addedFiles} PDF file(s) added successfully.`,
            "success"
        );

    }

}


// =====================================================
// DISPLAY FILES
// =====================================================

function displayFiles() {

    fileList.innerHTML = "";


    // No files
    if (files.length === 0) {

        fileList.innerHTML = `
            <div class="empty-message">

                <div class="empty-icon">
                    📄
                </div>

                <p>
                    No PDF files selected
                </p>

                <small>
                    Add at least two PDF files to merge
                </small>

            </div>
        `;

        fileCount.textContent = "0 files";

        mergeBtn.disabled = true;

        return;
    }


    // Update file count

    fileCount.textContent =
        `${files.length} file${files.length === 1 ? "" : "s"}`;


    // Create file items

    files.forEach(function (file, index) {

        const item = document.createElement("div");

        item.className = "file-item";


        item.innerHTML = `

            <div class="file-info">

                <div class="file-icon">
                    📄
                </div>

                <div class="file-details">

                    <div class="file-name">
                        ${escapeHTML(file.name)}
                    </div>

                    <div class="file-size">
                        ${formatFileSize(file.size)}
                    </div>

                </div>

            </div>


            <button
                type="button"
                class="remove-btn"
                onclick="removeFile(${index})"
                title="Remove file"
            >
                ✕
            </button>

        `;


        fileList.appendChild(item);

    });


    // Enable merge only if 2 or more files exist

    mergeBtn.disabled = files.length < 2;

}


// =====================================================
// REMOVE SINGLE FILE
// =====================================================

function removeFile(index) {

    if (index < 0 || index >= files.length) {
        return;
    }


    const removedFile = files[index];

    files.splice(index, 1);


    displayFiles();


    showMessage(
        `${removedFile.name} removed.`,
        "success"
    );

}


// =====================================================
// CLEAR ALL FILES
// =====================================================

clearBtn.addEventListener("click", function () {

    files = [];

    displayFiles();

    message.textContent = "";

    message.className = "message";

    downloadSection.style.display = "none";


    // Release previous object URL
    if (downloadBtn.href.startsWith("blob:")) {

        URL.revokeObjectURL(downloadBtn.href);

    }

    downloadBtn.href = "#";

});


// =====================================================
// MERGE PDF FILES
// =====================================================

mergeBtn.addEventListener("click", async function () {


    // Check minimum files

    if (files.length < 2) {

        showMessage(
            "❌ Please select at least 2 PDF files.",
            "error"
        );

        return;
    }


    // Disable button while processing

    mergeBtn.disabled = true;

    mergeBtn.textContent = "⏳ Merging...";


    showMessage(
        "Uploading PDFs and merging them...",
        "loading"
    );


    downloadSection.style.display = "none";


    // Create FormData

    const formData = new FormData();


    // Add every PDF

    files.forEach(function (file) {

        formData.append("files", file);

    });


    try {


        // =================================================
        // SEND REQUEST TO FASTAPI
        // =================================================

        const response = await fetch(
            `${API_URL}/merge`,
            {
                method: "POST",
                body: formData
            }
        );


        // =================================================
        // CHECK RESPONSE
        // =================================================

        if (!response.ok) {

            let errorMessage =
                `Server error: ${response.status}`;

            try {

                const errorData =
                    await response.json();

                if (errorData.detail) {

                    errorMessage =
                        errorData.detail;

                }

            } catch (error) {

                // Ignore JSON parsing error

            }


            throw new Error(errorMessage);
        }


        // =================================================
        // GET MERGED PDF
        // =================================================

        const blob =
            await response.blob();


        // Check response

        if (blob.size === 0) {

            throw new Error(
                "The server returned an empty PDF."
            );

        }


        // =================================================
        // CREATE DOWNLOAD URL
        // =================================================

        const downloadURL =
            URL.createObjectURL(blob);


        downloadBtn.href = downloadURL;

        downloadBtn.download = "merged.pdf";


        // =================================================
        // SHOW SUCCESS
        // =================================================

        downloadSection.style.display = "block";


        showMessage(
            "✅ PDFs merged successfully!",
            "success"
        );


        // Automatically scroll to download section

        downloadSection.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });


    } catch (error) {


        console.error(
            "PDF merge error:",
            error
        );


        showMessage(
            `❌ ${error.message}`,
            "error"
        );


    } finally {


        // Enable button again

        mergeBtn.disabled =
            files.length < 2;

        mergeBtn.textContent =
            "🔗 Merge PDFs";

    }

});


// =====================================================
// FORMAT FILE SIZE
// =====================================================

function formatFileSize(bytes) {

    if (bytes < 1024) {

        return `${bytes} B`;

    }


    if (bytes < 1024 * 1024) {

        return `${(bytes / 1024).toFixed(1)} KB`;

    }


    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;

}


// =====================================================
// SHOW MESSAGE
// =====================================================

function showMessage(text, type) {

    message.textContent = text;

    message.className =
        `message ${type}`;

}


// =====================================================
// ESCAPE HTML
// =====================================================

function escapeHTML(value) {

    const div =
        document.createElement("div");

    div.textContent = value;

    return div.innerHTML;

}


// =====================================================
// CHECK BACKEND STATUS
// =====================================================

async function checkBackend() {

    try {

        const response =
            await fetch(
                `${API_URL}/health`
            );


        if (response.ok) {

            console.log(
                "✅ PDF Merger backend is online."
            );

        } else {

            console.warn(
                "⚠ Backend returned an error."
            );

        }

    } catch (error) {

        console.warn(
            "⚠ Could not connect to PDF Merger backend.",
            error
        );

    }

}


// =====================================================
// START BACKEND CHECK
// =====================================================

checkBackend();

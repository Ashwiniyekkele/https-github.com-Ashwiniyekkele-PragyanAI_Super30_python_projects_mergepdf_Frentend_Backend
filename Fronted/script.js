```javascript
// ============================================================
// PragyanAI PDF Merger
// script.js
// ============================================================


// ============================================================
// FASTAPI BACKEND URL
// ============================================================

// LOCAL DEVELOPMENT
// const API_URL = "http://127.0.0.1:8000";

// PRODUCTION
// Replace this with your deployed FastAPI backend URL.

const API_URL =
    "https://your-fastapi-backend.onrender.com";

console.log("PDF Merger API URL:", API_URL);


// ============================================================
// DOM ELEMENTS
// ============================================================

const pdfFiles =
    document.getElementById("pdfFiles");

const mergeButton =
    document.getElementById("mergeButton");

const mergeMessage =
    document.getElementById("mergeMessage");

const fileList =
    document.getElementById("fileList");

const selectedFiles =
    document.getElementById("selectedFiles");

const resultContainer =
    document.getElementById("resultContainer");

const downloadButton =
    document.getElementById("downloadButton");

const apiStatus =
    document.getElementById("apiStatus");

const statusIndicator =
    document.getElementById("statusIndicator");

const swaggerLink =
    document.getElementById("swaggerLink");


// ============================================================
// APPLICATION STATE
// ============================================================

let mergedPDFBlob = null;
let mergedPDFURL = null;


// ============================================================
// INITIALIZE
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        checkAPIStatus();

        if (swaggerLink) {
            swaggerLink.href =
                `${API_URL}/docs`;
        }

    }
);


// ============================================================
// CHECK API STATUS
// ============================================================

async function checkAPIStatus() {

    try {

        apiStatus.textContent =
            "Checking backend...";

        statusIndicator.className =
            "status-indicator checking";


        const response =
            await fetch(
                `${API_URL}/health`
            );


        if (!response.ok) {

            throw new Error(
                "Backend returned an error."
            );

        }


        const result =
            await response.json();


        if (
            result.success === true ||
            result.status === "healthy"
        ) {

            apiStatus.textContent =
                "Backend API is online";

            statusIndicator.className =
                "status-indicator online";

        }

        else {
```

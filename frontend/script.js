const API_URL = "/api/interview";

let candidates = [];
let sessionId = null;
let questionNumber = 0;

// Elements
const candidateSection = document.getElementById("candidate-section");
const interviewSection = document.getElementById("interview-section");
const feedbackSection = document.getElementById("feedback-section");

const candidateSelect = document.getElementById("candidate-select");
const candidateInfo = document.getElementById("candidate-info");

const candidateName = document.getElementById("candidate-name");
const candidateRole = document.getElementById("candidate-role");
const candidateExperience = document.getElementById("candidate-experience");

const startBtn = document.getElementById("start-btn");
const submitBtn = document.getElementById("submit-btn");

const interviewRole = document.getElementById("interview-role");
const questionText = document.getElementById("question-text");
const questionNumberElement = document.getElementById("question-number");

const answerInput = document.getElementById("answer-input");
const loading = document.getElementById("loading");


// Load candidates from the provided data file
async function loadCandidates() {
    try {
        const response = await fetch("../data/candidates.json");

        if (!response.ok) {
            throw new Error("Could not load candidate data.");
        }

        const data = await response.json();
        candidates = data.candidates;

        candidates.forEach((candidate, index) => {
            const option = document.createElement("option");

            option.value = index;
            option.textContent =
                `${candidate.member.name} — ${candidate.member.jobRole}`;

            candidateSelect.appendChild(option);
        });

    } catch (error) {
        console.error(error);
        alert("Could not load candidate data.");
    }
}


// Display selected candidate information
candidateSelect.addEventListener("change", () => {
    const index = candidateSelect.value;

    if (index === "") {
        candidateInfo.classList.add("hidden");
        return;
    }

    const candidate = candidates[index];

    candidateName.textContent = candidate.member.name;
    candidateRole.textContent = candidate.member.jobRole;
    candidateExperience.textContent =
        `${candidate.member.yearsExperience} years of experience`;

    candidateInfo.classList.remove("hidden");
});


// Start interview
startBtn.addEventListener("click", async () => {
    const index = candidateSelect.value;

    if (index === "") {
        alert("Please select a candidate first.");
        return;
    }

    const candidate = candidates[index];

    sessionId = `frontend-${Date.now()}`;
    questionNumber = 1;

    startBtn.disabled = true;
    startBtn.textContent = "Starting interview...";

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                sessionId: sessionId,
                candidate: candidate
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || data.error || "Failed to start interview.");
        }

        candidateSection.classList.add("hidden");
        interviewSection.classList.remove("hidden");

        interviewRole.textContent = candidate.member.jobRole;
        questionText.textContent = data.reply;
        questionNumberElement.textContent = questionNumber;

    } catch (error) {
        console.error(error);
        alert(error.message);
    } finally {
        startBtn.disabled = false;
        startBtn.textContent = "Start Interview";
    }
});


// Submit candidate answer
submitBtn.addEventListener("click", async () => {
    const answer = answerInput.value.trim();

    if (!answer) {
        alert("Please enter your answer.");
        return;
    }

    submitBtn.disabled = true;
    answerInput.disabled = true;
    loading.classList.remove("hidden");

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                sessionId: sessionId,
                message: answer
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || data.error || "Failed to process answer.");
        }

        if (data.done) {
            showFeedback(data.feedback);
            return;
        }

        questionNumber++;
        questionNumberElement.textContent = questionNumber;
        questionText.textContent = data.reply;

        answerInput.value = "";

    } catch (error) {
        console.error(error);
        alert(error.message);

    } finally {
        submitBtn.disabled = false;
        answerInput.disabled = false;
        loading.classList.add("hidden");
    }
});


// Display final feedback
function showFeedback(feedback) {
    interviewSection.classList.add("hidden");
    feedbackSection.classList.remove("hidden");

    // Overall summary
    document.getElementById("feedback-summary").textContent =
        feedback.summary;

    // Calculate a simple deterministic readiness score.
    const strengths = feedback.strengths || [];
const gaps = feedback.gaps || [];
const nextSteps = feedback.next || [];

const performanceTitle =
    document.getElementById("performance-title");

const performanceStats =
    document.getElementById("performance-stats");

if (strengths.length > gaps.length) {
    performanceTitle.textContent =
        "Strong technical foundation";
} else if (strengths.length === gaps.length) {
    performanceTitle.textContent =
        "Solid foundation with room to grow";
} else {
    performanceTitle.textContent =
        "Developing technical foundation";
}

performanceStats.textContent =
    `${strengths.length} strengths • ${gaps.length} improvement areas • ${nextSteps.length} next steps`;

    // Helper to create interactive feedback cards
   function renderCards(containerId, items, type) {
    const container = document.getElementById(containerId);

    container.innerHTML = "";

    items.forEach(item => {
        const card = document.createElement("div");

        card.className = `feedback-card ${type}`;

        card.innerHTML = `
            <div class="feedback-card-header">

                <span class="feedback-icon">
                    ${
                        type === "strength"
                            ? "✓"
                            : type === "gap"
                                ? "⚠"
                                : "→"
                    }
                </span>

                <div class="feedback-card-content">

                    <span class="feedback-card-type">
                        ${
                            type === "strength"
                                ? "STRENGTH"
                                : type === "gap"
                                    ? "AREA TO IMPROVE"
                                    : "NEXT STEP"
                        }
                    </span>

                    <span class="feedback-card-text">
                        ${item}
                    </span>

                </div>

                <span class="feedback-arrow">↗</span>

            </div>
        `;

        container.appendChild(card);
    });
}

    renderCards(
        "feedback-strengths",
        strengths,
        "strength"
    );

    renderCards(
        "feedback-gaps",
        gaps,
        "gap"
    );

    renderCards(
        "feedback-next",
        nextSteps,
        "next"
    );
}
const feedbackTabs = document.querySelectorAll(".feedback-tab");
const feedbackTabContents = document.querySelectorAll(
    ".feedback-tab-content"
);

feedbackTabs.forEach(tab => {
    tab.addEventListener("click", () => {
        const target = tab.dataset.tab;

        feedbackTabs.forEach(item => {
            item.classList.remove("active");
        });

        feedbackTabContents.forEach(content => {
            content.classList.add("hidden");
            content.classList.remove("active");
        });

        tab.classList.add("active");

        const targetContent =
            document.getElementById(`tab-${target}`);

        targetContent.classList.remove("hidden");
        targetContent.classList.add("active");
    });
});


// Initialize
loadCandidates();
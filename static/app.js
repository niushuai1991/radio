let questions = [];
let currentIndex = 0;
let currentMode = "random";
let selectedAnswers = new Set();
let isAnswered = false;

const statsEl = document.getElementById("stats");
const questionContainer = document.getElementById("questionContainer");
const submitBtn = document.getElementById("submitBtn");
const nextBtn = document.getElementById("nextBtn");
const refreshBtn = document.getElementById("refreshBtn");
const resultEl = document.getElementById("result");

document.addEventListener("DOMContentLoaded", async () => {
    await loadStats();
    await loadQuestions("random");

    document.querySelectorAll(".mode-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            const mode = btn.dataset.mode;
            switchMode(mode);
        });
    });

    submitBtn.addEventListener("click", submitAnswer);
    nextBtn.addEventListener("click", nextQuestion);
    refreshBtn.addEventListener("click", () => loadQuestions(currentMode));
});

async function loadStats() {
    try {
        const res = await fetch("/api/stats");
        const stats = await res.json();

        statsEl.innerHTML = `
            <div class="stat-item">
                <span class="stat-value">${stats.total_questions}</span>
                <span class="stat-label">总题数</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">${stats.total_practiced}</span>
                <span class="stat-label">已练习</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">${stats.accuracy}%</span>
                <span class="stat-label">正确率</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">${stats.new_questions}</span>
                <span class="stat-label">新题</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">${stats.wrong_questions}</span>
                <span class="stat-label">错题</span>
            </div>
        `;
    } catch (error) {
        console.error("加载统计失败:", error);
    }
}

async function loadQuestions(mode) {
    currentMode = mode;
    currentIndex = 0;
    selectedAnswers.clear();
    isAnswered = false;

    document.querySelectorAll(".mode-btn").forEach((btn) => {
        btn.classList.toggle("active", btn.dataset.mode === mode);
    });

    questionContainer.innerHTML = '<div class="loading">加载中...</div>';
    hideResult();
    updateButtons();

    try {
        const res = await fetch(`/api/questions?mode=${mode}&limit=20`);
        const data = await res.json();

        questions = data.questions;

        if (questions.length === 0) {
            showNoQuestions();
            return;
        }

        showQuestion();
    } catch (error) {
        questionContainer.innerHTML = '<div class="no-questions">加载失败，请重试</div>';
        console.error("加载题目失败:", error);
    }
}

function showQuestion() {
    if (currentIndex >= questions.length) {
        questionContainer.innerHTML = '<div class="no-questions">本组题目已完成！</div>';
        return;
    }

    const q = questions[currentIndex];
    selectedAnswers.clear();
    isAnswered = false;
    hideResult();
    updateButtons();

    const isMultiple = q.correct_answer.length > 1;

    questionContainer.innerHTML = `
        <div class="question">
            <div class="question-header">
                <span>题号: ${q.question_id}</span>
                <span>${isMultiple ? "多选题" : "单选题"}</span>
            </div>
            <div class="question-content">${q.content}</div>
            <div class="options">
                ${Object.entries(q.options)
                    .sort(([a], [b]) => a.localeCompare(b))
                    .map(([key, value]) => `
                    <div class="option" data-option="${key}">
                        <div class="option-label">${key}</div>
                        <div class="option-text">${value}</div>
                    </div>
                `).join("")}
            </div>
        </div>
    `;

    questionContainer.querySelectorAll(".option").forEach((option) => {
        option.addEventListener("click", () => selectOption(option.dataset.option));
    });
}

function selectOption(option) {
    if (isAnswered) return;

    const q = questions[currentIndex];
    const isMultiple = q.correct_answer.length > 1;

    if (isMultiple) {
        if (selectedAnswers.has(option)) {
            selectedAnswers.delete(option);
        } else {
            selectedAnswers.add(option);
        }
    } else {
        selectedAnswers.clear();
        selectedAnswers.add(option);
    }

    updateOptionSelection();
    submitBtn.disabled = selectedAnswers.size === 0;
}

function updateOptionSelection() {
    questionContainer.querySelectorAll(".option").forEach((el) => {
        const option = el.dataset.option;
        el.classList.toggle("selected", selectedAnswers.has(option));
    });
}

async function submitAnswer() {
    if (selectedAnswers.size === 0 || isAnswered) return;

    const q = questions[currentIndex];
    const userAnswer = Array.from(selectedAnswers).sort().join("");

    try {
        const res = await fetch("/api/submit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question_id: q.question_id,
                answer: userAnswer,
            }),
        });

        const result = await res.json();
        isAnswered = true;

        showResult(result, q.correct_answer);
        updateButtons();
        await loadStats();
    } catch (error) {
        console.error("提交答案失败:", error);
    }
}

function showResult(result, correctAnswer) {
    const isCorrect = result.is_correct;

    questionContainer.querySelectorAll(".option").forEach((el) => {
        const option = el.dataset.option;

        if (correctAnswer.includes(option)) {
            el.classList.add("correct");
        }

        if (selectedAnswers.has(option) && !correctAnswer.includes(option)) {
            el.classList.add("wrong");
        }
    });

    resultEl.className = `result show ${isCorrect ? "success" : "error"}`;
    resultEl.innerHTML = isCorrect
        ? "✓ 回答正确！"
        : `✗ 回答错误，正确答案是：${correctAnswer}`;
}

function hideResult() {
    resultEl.className = "result";
}

function nextQuestion() {
    currentIndex++;
    showQuestion();
}

function updateButtons() {
    submitBtn.disabled = selectedAnswers.size === 0 || isAnswered;
    nextBtn.disabled = !isAnswered || currentIndex >= questions.length - 1;
}

function switchMode(mode) {
    if (mode !== currentMode) {
        loadQuestions(mode);
    }
}

function showNoQuestions() {
    const messages = {
        random: "暂无题目",
        new: "🎉 恭喜！您已练习完所有题目",
        wrong: "太棒了！没有错题",
    };

    questionContainer.innerHTML = `<div class="no-questions">${messages[currentMode]}</div>`;
    submitBtn.disabled = true;
    nextBtn.disabled = true;
}

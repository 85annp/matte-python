let pyodide = null;
let currentUserId = null;
let lessonsData = [];
let editors = {}; // task_id -> CodeMirror instance
let activitiesData = [];
let activityEditors = {};

// Initialize UUID
async function initUser() {
    let urlParams = new URLSearchParams(window.location.search);
    let idFromUrl = urlParams.get('id');

    if (idFromUrl) {
        currentUserId = idFromUrl;
        localStorage.setItem('matte_python_id', currentUserId);
        // Clean URL without reloading
        window.history.replaceState({}, document.title, window.location.pathname);
    } else {
        currentUserId = localStorage.getItem('matte_python_id');
    }

    if (!currentUserId) {
        // Create new user on server
        await createNewUser();
    } else {
        // Verify user exists, if not, maybe it was wiped on server? 
        try {
            const res = await fetch(`/api/users/${currentUserId}`);
            const exists = await res.json();
            if (!exists) {
                await createNewUser();
            }
        } catch (e) {
            console.error("Fel vid verifiering av användare", e);
        }
    }
    
    const sidebarLinkInput = document.getElementById('sidebarLinkInput');
    if (sidebarLinkInput) {
        sidebarLinkInput.value = getUniqueLink();
    }
}

async function createNewUser() {
    try {
        const response = await fetch('/api/users', { method: 'POST' });
        currentUserId = await response.json();
        localStorage.setItem('matte_python_id', currentUserId);
        showLinkModal();
    } catch (e) {
        console.error("Kunde inte skapa användare", e);
    }
}

function getUniqueLink() {
    const baseUrl = window.location.origin + window.location.pathname;
    return `${baseUrl}?id=${currentUserId}`;
}

function showLinkModal() {
    const modal = document.getElementById('linkModal');
    const input = document.getElementById('uniqueLinkInput');
    input.value = getUniqueLink();
    modal.classList.remove('hidden');
}

// Setup Event Listeners
document.getElementById('copySidebarLinkBtn').addEventListener('click', () => {
    const input = document.getElementById('sidebarLinkInput');
    input.select();
    document.execCommand('copy');
    const btn = document.getElementById('copySidebarLinkBtn');
    btn.innerText = 'Kopierad!';
    setTimeout(() => { btn.innerText = 'Kopiera'; }, 2000);
});
document.getElementById('closeModalBtn').addEventListener('click', () => {
    document.getElementById('linkModal').classList.add('hidden');
});
document.getElementById('copyLinkBtn').addEventListener('click', () => {
    const input = document.getElementById('uniqueLinkInput');
    input.select();
    document.execCommand('copy');
    const btn = document.getElementById('copyLinkBtn');
    btn.innerText = 'Kopierad!';
    setTimeout(() => { btn.innerText = 'Kopiera'; }, 2000);
});

// Initialize Pyodide
async function initPyodide() {
    const statusEl = document.getElementById('pyodideStatus');
    try {
        pyodide = await loadPyodide();
        await pyodide.loadPackage(['numpy', 'matplotlib']);
        // Redirect stdout to our own function
        pyodide.setStdout({ batched: (msg) => { window.currentStdout += msg + "\n"; } });

        // Override Python's input() to use browser prompt
        // Override matplotlib's show() to save the plot as an image instead of appending to body
        await pyodide.runPythonAsync(`
import builtins
import js
import os

os.environ['MPLBACKEND'] = 'Agg'

def custom_input(prompt=""):
    res = js.prompt(prompt)
    if res is None:
        raise EOFError("Inmatning avbröts av användaren")
    print(str(prompt) + str(res))
    return res

builtins.input = custom_input

try:
    import matplotlib.pyplot as plt
    def custom_show(*args, **kwargs):
        plt.savefig('plot.png', bbox_inches='tight')
        plt.clf()
    plt.show = custom_show
except ImportError:
    pass
        `);

        statusEl.textContent = "Python är redo!";
        statusEl.className = "status-badge ready";
        setTimeout(() => { statusEl.style.display = 'none'; }, 2000);
    } catch (err) {
        statusEl.textContent = "Fel vid laddning av Python";
        statusEl.className = "status-badge error";
        console.error(err);
    }
}

// Fetch Lessons
async function loadLessons() {
    try {
        const response = await fetch('/api/lessons');
        lessonsData = await response.json();
        renderSidebar();
    } catch (e) {
        console.error("Kunde inte ladda lektioner", e);
        document.getElementById('lessonList').innerHTML = '<div class="nav-loading">Fel vid laddning</div>';
    }
}

// Render Sidebar
function renderSidebar() {
    const nav = document.getElementById('lessonList');
    nav.innerHTML = '';

    lessonsData.forEach(lesson => {
        const el = document.createElement('div');
        el.className = 'nav-item';
        el.textContent = lesson.title;
        el.addEventListener('click', () => openLesson(lesson));
        nav.appendChild(el);
    });
}

function sortTasks(tasks) {
    return [...tasks].sort((a, b) => {
        if (a.task_number !== b.task_number) {
            return a.task_number - b.task_number;
        }

        return a.id - b.id;
    });
}

async function renderMath() {
    if (window.MathJax && MathJax.typesetPromise) {
        try {
            await MathJax.typesetPromise();
        } catch (e) {
            console.error('MathJax render error:', e);
        }
    }
}

function findPyodideImageFile() {
    try {
        const files = pyodide.FS.readdir('.');
        return files.find(name => name.endsWith('.png') || name.endsWith('.svg')) || null;
    } catch (e) {
        return null;
    }
}

function getPyodideImageUrl() {
    const imageFile = findPyodideImageFile();
    if (!imageFile) return null;

    try {
        const data = pyodide.FS.readFile(imageFile);
        const mimeType = imageFile.endsWith('.svg') ? 'image/svg+xml' : 'image/png';
        return URL.createObjectURL(new Blob([data], { type: mimeType }));
    } catch (e) {
        return null;
    }
}

// Open Lesson
async function openLesson(lesson) {
    // Update active class
    document.querySelectorAll('.nav-item').forEach(el => {
        if (el.textContent === lesson.title) el.classList.add('active');
        else el.classList.remove('active');
    });

    const contentArea = document.getElementById('contentArea');

    // Fetch user's saved code
    let savedCodes = {};
    try {
        const res = await fetch(`/api/saved_code/${currentUserId}`);
        const data = await res.json();
        data.forEach(item => { savedCodes[item.task_id] = item.code; });
    } catch (e) {
        console.error(e);
    }

    let html = `
        <div class="lesson-container">
            <h2>${lesson.title}</h2>
            <div class="theory-box">
                ${lesson.theory_content}
            </div>
            <div class="task-list">
    `;

    // Group tasks by level
    const level1 = sortTasks(lesson.tasks.filter(t => t.level === 1));
    const level2 = sortTasks(lesson.tasks.filter(t => t.level === 2));

    if (level1.length > 0) {
        html += `<h3 class="level-heading">Nivå 1</h3>`;
        level1.forEach(task => { html += createTaskCard(task, savedCodes[task.id]); });
    }

    if (level2.length > 0) {
        html += `<h3 class="level-heading">Nivå 2</h3>`;
        level2.forEach(task => { html += createTaskCard(task, savedCodes[task.id]); });
    }

    html += `</div></div>`;
    contentArea.innerHTML = html;
    document.querySelector('.main-content').scrollTop = 0;
    window.scrollTo(0, 0);
    if (typeof closeMobileMenu === 'function') closeMobileMenu();
    if (window.hljs) {
        contentArea.querySelectorAll('pre code').forEach((block) => {
            delete block.dataset.highlighted;
            window.hljs.highlightElement(block);
        });
    }
    await renderMath();

    // Initialize CodeMirror instances
    editors = {};
    lesson.tasks.forEach(task => {
        const textarea = document.getElementById(`editor-${task.id}`);
        if (textarea) {
            const editor = CodeMirror.fromTextArea(textarea, {
                mode: "python",
                theme: "dracula",
                lineNumbers: true,
                indentUnit: 4,
                matchBrackets: true
            });

            // Auto-save typing after delay
            let timeout = null;
            editor.on('change', () => {
                clearTimeout(timeout);
                timeout = setTimeout(() => saveTaskCode(task.id, editor.getValue()), 1000);
            });

            editors[task.id] = editor;
        }
    });
}

function createTaskCard(task, savedCode) {
    const code = savedCode !== undefined ? savedCode : task.default_code;
    return `
        <div class="task-card">
            <div class="task-prompt">
                <div class="task-prompt-header">
                    <span class="task-number-badge">Uppgift ${task.task_number}</span>
                </div>
                <div class="task-prompt-text">${task.prompt}</div>
            </div>
            <div class="editor-container">
                <textarea id="editor-${task.id}">${code}</textarea>
            </div>
            <div class="task-actions">
                <button class="btn btn-primary" onclick="runCode(${task.id})">▶ Kör Kod</button>
                <button class="btn btn-secondary" onclick="openPythonTutor(${task.id})">🐛 Stega i Python Tutor</button>
            </div>
            <div id="output-${task.id}" class="output-container"></div>
        </div>
    `;
}

// Run Python Code
async function runCode(taskId) {
    const outputEl = document.getElementById(`output-${taskId}`);
    outputEl.className = 'output-container has-content';

    if (!pyodide) {
        outputEl.innerHTML = '<i>Väntar på att Python ska laddas...</i>';
        return;
    }

    const code = editors[taskId].getValue();
    window.currentStdout = ""; // Reset custom stdout buffer

    try { pyodide.FS.unlink('plot.png'); } catch (e) { }
    try { pyodide.FS.unlink('figure.png'); } catch (e) { }
    try { pyodide.FS.unlink('output.png'); } catch (e) { }

    outputEl.innerHTML = '<i>Kör...</i>';

    try {
        await pyodide.runPythonAsync(code);
        outputEl.className = 'output-container has-content';
        const imageUrl = getPyodideImageUrl();

        if (imageUrl) {
            outputEl.innerHTML = '';
            const img = document.createElement('img');
            img.src = imageUrl;
            img.className = 'output-image';
            outputEl.appendChild(img);
            if (window.currentStdout) {
                const pre = document.createElement('pre');
                pre.textContent = window.currentStdout;
                outputEl.appendChild(pre);
            }
        } else if (window.currentStdout) {
            outputEl.textContent = window.currentStdout;
        } else {
            outputEl.innerHTML = '<i>Koden kördes utan utskrifter.</i>';
        }
    } catch (err) {
        outputEl.className = 'output-container has-content error';

        // Make error message cleaner for high school students
        let errorMsg = err.toString();
        // Remove the traceback lines that point to pyodide internals
        let cleanError = errorMsg.split('\\n').filter(line => !line.includes('File "<exec>"') && !line.includes('File "<string>"')).join('\\n');

        outputEl.textContent = cleanError || errorMsg;
    }
}

// Open in Python Tutor
function openPythonTutor(taskId) {
    const code = editors[taskId].getValue();
    const encodedCode = encodeURIComponent(code);
    const url = `https://pythontutor.com/visualize.html#code=${encodedCode}&cumulative=false&mode=display&origin=opt-frontend.js&py=3&rawInputLstJSON=%5B%5D&tc=undefined`;
    window.open(url, '_blank');
}

// Save Code to Server
async function saveTaskCode(taskId, code) {
    try {
        await fetch('/api/saved_code', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: currentUserId,
                task_id: taskId,
                code: code
            })
        });
        console.log(`Saved task ${taskId}`);
    } catch (e) {
        console.error("Fel vid sparande", e);
    }
}

// Boot up
window.onload = async () => {
    await initUser();
    loadLessons();
    loadActivities();
    initPyodide();
};

async function loadActivities() {
    try {
        const response = await fetch('/api/activities');
        activitiesData = await response.json();
        renderActivitySidebar();
    } catch (e) {
        console.error("Kunde inte ladda aktiviteter", e);
    }
}

function renderActivitySidebar() {
    const nav = document.getElementById('activityList');
    if (!nav) return;
    nav.innerHTML = '';

    activitiesData.forEach(activity => {
        const el = document.createElement('div');
        el.className = 'nav-item';
        el.textContent = activity.title;
        el.addEventListener('click', () => openActivity(activity));
        nav.appendChild(el);
    });
}

async function openActivity(activity) {
    document.querySelectorAll('.nav-item').forEach(el => {
        if (el.textContent === activity.title) el.classList.add('active');
        else el.classList.remove('active');
    });

    const contentArea = document.getElementById('contentArea');

    let state = { code: "", answers: {} };
    try {
        const res = await fetch(`/api/activities/state/${currentUserId}/${activity.id}`);
        state = await res.json();
    } catch (e) {
        console.error(e);
    }

    let code = state.code || activity.default_code;

    let html = `
        <div class="lesson-container">
            <h2>${activity.title}</h2>
            <div class="theory-box">
                ${activity.description}
            </div>
            
            <div class="task-card">
                <h3 style="margin-top: 0;">1. Programmera här</h3>
                <p style="color: #a1a1aa; font-size: 0.9rem; margin-bottom: 10px;">Skriv ditt program som löser aktivitetens problemställning.</p>
                <div class="editor-container">
                    <textarea id="activity-editor-${activity.id}">${code}</textarea>
                </div>
                <div class="task-actions">
                    <button class="btn btn-primary" onclick="runActivityCode(${activity.id})">▶ Kör Kod</button>
                </div>
                <div id="activity-output-${activity.id}" class="output-container"></div>
            </div>

            <div class="task-card">
                <h3 style="margin-top: 0;">2. Svara på frågorna</h3>
                <p style="color: #a1a1aa; font-size: 0.9rem; margin-bottom: 20px;">Använd ditt program för att räkna ut svaren.</p>
                <div id="activity-questions-${activity.id}">
                    ${activity.questions.map((q, idx) => {
                        let answer = state.answers[q.id] || '';
                        let feedbackText = '';
                        let feedbackColor = '';
                        if (answer) {
                            if (answer.trim() === q.correct_answer || answer.trim().replace(',', '.') === q.correct_answer) {
                                feedbackText = "Rätt!";
                                feedbackColor = "#4ade80";
                            } else {
                                feedbackText = "Försök igen!";
                                feedbackColor = "#f87171";
                            }
                        }
                        return `
                        <div class="question-item" style="margin-bottom: 15px;">
                            <div style="margin-bottom: 5px; color: #e2e8f0; font-size: 0.95rem;">${idx + 1}. ${q.prompt}</div>
                            <div style="display: flex; gap: 10px;">
                                <input type="text" id="q-${q.id}" class="activity-input" style="flex: 1; background: #1e293b; border: 1px solid #334155; color: #f8fafc; padding: 8px 12px; border-radius: 6px;" value="${answer}">
                                <button class="btn btn-outline" onclick="checkAnswer(${q.id}, '${q.correct_answer}', ${activity.id})">Rätta</button>
                            </div>
                            <div id="feedback-${q.id}" style="margin-top: 5px; font-size: 0.85rem; color: ${feedbackColor};">${feedbackText}</div>
                        </div>
                        `;
                    }).join('')}
                </div>
            </div>
        </div>
    `;

    contentArea.innerHTML = html;
    document.querySelector('.main-content').scrollTop = 0;
    window.scrollTo(0, 0);
    if (typeof closeMobileMenu === 'function') closeMobileMenu();
    if (window.hljs) {
        contentArea.querySelectorAll('pre code').forEach((block) => {
            delete block.dataset.highlighted;
            window.hljs.highlightElement(block);
        });
    }
    await renderMath();

    const textarea = document.getElementById(`activity-editor-${activity.id}`);
    if (textarea) {
        const editor = CodeMirror.fromTextArea(textarea, {
            mode: "python",
            theme: "dracula",
            lineNumbers: true,
            indentUnit: 4,
            matchBrackets: true
        });

        let timeout = null;
        editor.on('change', () => {
            clearTimeout(timeout);
            timeout = setTimeout(() => saveActivityState(activity.id), 1000);
        });

        activityEditors[activity.id] = editor;
    }
}

function checkAnswer(qId, correct, activityId) {
    const input = document.getElementById(`q-${qId}`).value.trim();
    const feedback = document.getElementById(`feedback-${qId}`);
    if (input === correct || input.replace(',', '.') === correct) {
        feedback.textContent = "Rätt!";
        feedback.style.color = "#4ade80";
    } else {
        feedback.textContent = "Försök igen!";
        feedback.style.color = "#f87171";
    }
    
    if (activityId) {
        saveActivityState(activityId);
    }
}

async function runActivityCode(activityId) {
    const outputEl = document.getElementById(`activity-output-${activityId}`);
    outputEl.className = 'output-container has-content';

    if (!pyodide) {
        outputEl.innerHTML = '<i>Väntar på att Python ska laddas...</i>';
        return;
    }

    const code = activityEditors[activityId].getValue();
    window.currentStdout = "";

    outputEl.innerHTML = '<i>Kör...</i>';

    try { pyodide.FS.unlink('plot.png'); } catch (e) { }
    try { pyodide.FS.unlink('figure.png'); } catch (e) { }
    try { pyodide.FS.unlink('output.png'); } catch (e) { }

    try {
        await pyodide.runPythonAsync(code);
        outputEl.className = 'output-container has-content';
        const imageUrl = getPyodideImageUrl();

        if (imageUrl) {
            outputEl.innerHTML = '';
            const img = document.createElement('img');
            img.src = imageUrl;
            img.className = 'output-image';
            outputEl.appendChild(img);
            if (window.currentStdout) {
                const pre = document.createElement('pre');
                pre.textContent = window.currentStdout;
                outputEl.appendChild(pre);
            }
        } else if (window.currentStdout) {
            outputEl.textContent = window.currentStdout;
        } else {
            outputEl.innerHTML = '<i>Koden kördes utan utskrifter.</i>';
        }
    } catch (err) {
        outputEl.className = 'output-container has-content error';
        let errorMsg = err.toString();
        let cleanError = errorMsg.split('\\n').filter(line => !line.includes('File "<exec>"') && !line.includes('File "<string>"')).join('\\n');
        outputEl.textContent = cleanError || errorMsg;
    }
}

async function saveActivityState(activityId) {
    const activity = activitiesData.find(a => a.id === activityId);
    if (!activity) return;

    let answers = {};
    activity.questions.forEach(q => {
        const input = document.getElementById(`q-${q.id}`);
        if (input) answers[q.id] = input.value;
    });

    const code = activityEditors[activityId].getValue();

    try {
        await fetch('/api/activities/state', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: currentUserId,
                activity_id: activityId,
                answers: answers,
                code: code
            })
        });
    } catch (e) {
        console.error(e);
    }
}

// Mobile Menu Logic
function closeMobileMenu() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (sidebar && overlay) {
        sidebar.classList.remove('open');
        overlay.classList.remove('active');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    if (mobileMenuBtn && sidebar && overlay) {
        mobileMenuBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            overlay.classList.toggle('active');
        });

        overlay.addEventListener('click', closeMobileMenu);
    }
});

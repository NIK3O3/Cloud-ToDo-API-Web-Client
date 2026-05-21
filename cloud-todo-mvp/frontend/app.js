const state = {
  apiBaseUrl: localStorage.getItem("apiBaseUrl") || "http://localhost:8000",
  apiKey: localStorage.getItem("apiKey") || "dev-api-key",
};

const elements = {
  apiBaseUrl: document.querySelector("#apiBaseUrl"),
  apiKey: document.querySelector("#apiKey"),
  saveConfigButton: document.querySelector("#saveConfigButton"),
  taskForm: document.querySelector("#taskForm"),
  title: document.querySelector("#title"),
  description: document.querySelector("#description"),
  priority: document.querySelector("#priority"),
  dueDate: document.querySelector("#dueDate"),
  statusFilter: document.querySelector("#statusFilter"),
  priorityFilter: document.querySelector("#priorityFilter"),
  refreshButton: document.querySelector("#refreshButton"),
  taskList: document.querySelector("#taskList"),
  totalCount: document.querySelector("#totalCount"),
  message: document.querySelector("#message"),
};

elements.apiBaseUrl.value = state.apiBaseUrl;
elements.apiKey.value = state.apiKey;

function showMessage(message = "") {
  elements.message.textContent = message;
}

function buildUrl(path, params = {}) {
  const url = new URL(`${state.apiBaseUrl.replace(/\/$/, "")}${path}`);
  Object.entries(params)
    .filter(([, value]) => value !== "" && value !== undefined && value !== null)
    .forEach(([key, value]) => url.searchParams.set(key, value));
  return url;
}

async function apiFetch(path, options = {}) {
  const response = await fetch(buildUrl(path, options.params), {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": state.apiKey,
      ...(options.headers || {}),
    },
  });

  if (response.status === 204) {
    return null;
  }

  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.message || "API request failed");
  }
  return body;
}

function taskTemplate(task) {
  return `
    <article class="task-card">
      <div>
        <h3>${escapeHtml(task.title)}</h3>
        <p>${escapeHtml(task.description || "Без опису")}</p>
        <div class="meta">Due: ${task.dueDate || "—"} · Updated: ${new Date(task.updatedAt).toLocaleString()}</div>
        <div class="badges">
          <span class="badge">${task.status}</span>
          <span class="badge">${task.priority}</span>
        </div>
      </div>
      <div class="card-actions">
        <select data-status-for="${task.id}">
          ${["NEW", "IN_PROGRESS", "DONE"].map((status) => `<option value="${status}" ${status === task.status ? "selected" : ""}>${status}</option>`).join("")}
        </select>
        <button class="secondary" data-delete-for="${task.id}" type="button">Видалити</button>
      </div>
    </article>
  `;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function loadTasks() {
  try {
    showMessage();
    const body = await apiFetch("/api/tasks", {
      params: {
        status: elements.statusFilter.value,
        priority: elements.priorityFilter.value,
        limit: 50,
        offset: 0,
      },
    });
    elements.totalCount.textContent = body.total;
    elements.taskList.innerHTML = body.items.length ? body.items.map(taskTemplate).join("") : "<p>Задач поки немає.</p>";
  } catch (error) {
    showMessage(error.message);
  }
}

async function createTask(event) {
  event.preventDefault();
  try {
    await apiFetch("/api/tasks", {
      method: "POST",
      body: JSON.stringify({
        title: elements.title.value,
        description: elements.description.value || null,
        priority: elements.priority.value,
        dueDate: elements.dueDate.value || null,
      }),
    });
    elements.taskForm.reset();
    elements.priority.value = "MEDIUM";
    await loadTasks();
  } catch (error) {
    showMessage(error.message);
  }
}

async function handleTaskListChange(event) {
  const taskId = event.target.dataset.statusFor;
  if (!taskId) return;
  try {
    await apiFetch(`/api/tasks/${taskId}`, {
      method: "PATCH",
      body: JSON.stringify({ status: event.target.value }),
    });
    await loadTasks();
  } catch (error) {
    showMessage(error.message);
  }
}

async function handleTaskListClick(event) {
  const taskId = event.target.dataset.deleteFor;
  if (!taskId) return;
  try {
    await apiFetch(`/api/tasks/${taskId}`, { method: "DELETE" });
    await loadTasks();
  } catch (error) {
    showMessage(error.message);
  }
}

elements.saveConfigButton.addEventListener("click", () => {
  state.apiBaseUrl = elements.apiBaseUrl.value.trim();
  state.apiKey = elements.apiKey.value.trim();
  localStorage.setItem("apiBaseUrl", state.apiBaseUrl);
  localStorage.setItem("apiKey", state.apiKey);
  loadTasks();
});

elements.taskForm.addEventListener("submit", createTask);
elements.refreshButton.addEventListener("click", loadTasks);
elements.statusFilter.addEventListener("change", loadTasks);
elements.priorityFilter.addEventListener("change", loadTasks);
elements.taskList.addEventListener("change", handleTaskListChange);
elements.taskList.addEventListener("click", handleTaskListClick);

loadTasks();

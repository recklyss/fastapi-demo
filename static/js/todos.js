const TodoApp = (() => {
  function requireAuth() {
    if (!TodoApi.getAccessToken()) {
      window.location.href = "/login";
      return false;
    }
    return true;
  }

  function showError(message) {
    const el = document.getElementById("todo-error");
    if (!el) {
      return;
    }
    el.hidden = !message;
    el.textContent = message || "";
  }

  function renderTodos(todos) {
    const list = document.getElementById("todo-list");
    const empty = document.getElementById("todo-empty");
    if (!list || !empty) {
      return;
    }
    list.innerHTML = "";
    empty.hidden = todos.length > 0;

    for (const todo of todos) {
      const item = document.createElement("li");
      item.className = `todo-item${todo.completed ? " done" : ""}`;
      item.dataset.id = todo.id;

      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.checked = todo.completed;
      checkbox.setAttribute("aria-label", "Mark completed");
      checkbox.addEventListener("change", async () => {
        showError("");
        try {
          await TodoApi.updateTodo(todo.id, { completed: checkbox.checked });
          await loadTodos();
        } catch (error) {
          showError(error.message || "Could not update todo");
          checkbox.checked = !checkbox.checked;
        }
      });

      const title = document.createElement("span");
      title.className = "todo-title";
      title.textContent = todo.title;

      const remove = document.createElement("button");
      remove.type = "button";
      remove.className = "btn ghost tiny";
      remove.textContent = "Delete";
      remove.addEventListener("click", async () => {
        showError("");
        try {
          await TodoApi.deleteTodo(todo.id);
          await loadTodos();
        } catch (error) {
          showError(error.message || "Could not delete todo");
        }
      });

      item.append(checkbox, title, remove);
      list.append(item);
    }
  }

  async function loadTodos() {
    const todos = await TodoApi.listTodos();
    renderTodos(todos);
  }

  function fillProfileChip(user) {
    const avatar = document.getElementById("profile-avatar");
    const name = document.getElementById("profile-name");
    if (!avatar || !name) {
      return;
    }
    const label = user.full_name || user.username || "Profile";
    const initial = String(label).trim().charAt(0).toUpperCase() || "?";
    avatar.textContent = initial;
    name.textContent = label;
  }

  async function init() {
    if (!requireAuth()) {
      return;
    }

    document.getElementById("logout-btn").addEventListener("click", () => {
      TodoApi.clearTokens();
      window.location.href = "/login";
    });

    const form = document.getElementById("todo-form");
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      showError("");
      const input = document.getElementById("todo-title");
      const title = input.value.trim();
      if (!title) {
        showError("Title cannot be blank");
        return;
      }
      const button = form.querySelector('button[type="submit"]');
      button.disabled = true;
      try {
        await TodoApi.createTodo(title);
        input.value = "";
        await loadTodos();
      } catch (error) {
        showError(error.message || "Could not add todo");
      } finally {
        button.disabled = false;
        input.focus();
      }
    });

    try {
      const user = await TodoApi.me();
      fillProfileChip(user);
    } catch (error) {
      console.error("Could not load profile chip", error);
    }

    try {
      await loadTodos();
    } catch (error) {
      showError(error.message || "Could not load todos");
    }
  }

  return { init };
})();

const TodoApi = (() => {
  const ACCESS_KEY = "todo_access_token";
  const REFRESH_KEY = "todo_refresh_token";

  function getAccessToken() {
    return localStorage.getItem(ACCESS_KEY);
  }

  function getRefreshToken() {
    return localStorage.getItem(REFRESH_KEY);
  }

  function setTokens({ access_token, refresh_token }) {
    localStorage.setItem(ACCESS_KEY, access_token);
    if (refresh_token) {
      localStorage.setItem(REFRESH_KEY, refresh_token);
    }
  }

  function clearTokens() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  }

  async function parseError(response) {
    try {
      const data = await response.json();
      if (typeof data.detail === "string") {
        return data.detail;
      }
      if (Array.isArray(data.detail)) {
        return data.detail.map((item) => item.msg || JSON.stringify(item)).join("; ");
      }
      return JSON.stringify(data);
    } catch {
      return `Request failed (${response.status})`;
    }
  }

  async function request(path, options = {}) {
    const headers = new Headers(options.headers || {});
    if (options.json !== undefined) {
      headers.set("Content-Type", "application/json");
    }
    if (options.auth) {
      const token = getAccessToken();
      if (!token) {
        throw new Error("Not signed in");
      }
      headers.set("Authorization", `Bearer ${token}`);
    }

    const response = await fetch(path, {
      ...options,
      headers,
      body: options.json !== undefined ? JSON.stringify(options.json) : options.body,
    });

    if (response.status === 401 && options.auth) {
      clearTokens();
      window.location.href = "/login";
      throw new Error("Session expired");
    }

    if (!response.ok) {
      throw new Error(await parseError(response));
    }

    if (response.status === 204) {
      return null;
    }

    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      return response.json();
    }
    return response.text();
  }

  function register(username, password) {
    return request("/auth/register", {
      method: "POST",
      json: { username, password },
    });
  }

  function login(username, password) {
    const body = new URLSearchParams({
      username,
      password,
    });
    return request("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
  }

  function me() {
    return request("/user/me", { auth: true });
  }

  function listTodos() {
    return request("/todos", { auth: true });
  }

  function createTodo(title) {
    return request("/todos", {
      method: "POST",
      auth: true,
      json: { title },
    });
  }

  function updateTodo(id, patch) {
    return request(`/todos/${id}`, {
      method: "PATCH",
      auth: true,
      json: patch,
    });
  }

  function deleteTodo(id) {
    return request(`/todos/${id}`, {
      method: "DELETE",
      auth: true,
    });
  }

  return {
    getAccessToken,
    getRefreshToken,
    setTokens,
    clearTokens,
    register,
    login,
    me,
    listTodos,
    createTodo,
    updateTodo,
    deleteTodo,
  };
})();

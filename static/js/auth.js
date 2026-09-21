const TodoAuth = (() => {
  function showError(message) {
    const el = document.getElementById("auth-error");
    if (!el) {
      return;
    }
    el.hidden = !message;
    el.textContent = message || "";
  }

  function redirectIfSignedIn() {
    if (TodoApi.getAccessToken()) {
      window.location.href = "/app";
    }
  }

  function initLogin() {
    redirectIfSignedIn();
    const form = document.getElementById("login-form");
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      showError("");
      const data = new FormData(form);
      const username = String(data.get("username") || "").trim();
      const password = String(data.get("password") || "");
      const button = form.querySelector('button[type="submit"]');
      button.disabled = true;
      try {
        const tokens = await TodoApi.login(username, password);
        TodoApi.setTokens(tokens);
        window.location.href = "/app";
      } catch (error) {
        showError(error.message || "Sign in failed");
      } finally {
        button.disabled = false;
      }
    });
  }

  function initRegister() {
    redirectIfSignedIn();
    const form = document.getElementById("register-form");
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      showError("");
      const data = new FormData(form);
      const username = String(data.get("username") || "").trim();
      const password = String(data.get("password") || "");
      const button = form.querySelector('button[type="submit"]');
      button.disabled = true;
      try {
        await TodoApi.register(username, password);
        const tokens = await TodoApi.login(username, password);
        TodoApi.setTokens(tokens);
        window.location.href = "/app";
      } catch (error) {
        showError(error.message || "Registration failed");
      } finally {
        button.disabled = false;
      }
    });
  }

  return { initLogin, initRegister };
})();

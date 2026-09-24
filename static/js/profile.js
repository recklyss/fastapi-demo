const TodoProfile = (() => {
  function requireAuth() {
    if (!TodoApi.getAccessToken()) {
      window.location.href = "/login";
      return false;
    }
    return true;
  }

  function showError(message) {
    const el = document.getElementById("profile-error");
    const ok = document.getElementById("profile-success");
    if (ok) {
      ok.hidden = true;
    }
    if (!el) {
      return;
    }
    el.hidden = !message;
    el.textContent = message || "";
  }

  function showSuccess() {
    const el = document.getElementById("profile-success");
    const err = document.getElementById("profile-error");
    if (err) {
      err.hidden = true;
    }
    if (!el) {
      return;
    }
    el.hidden = false;
  }

  function fillForm(user) {
    document.getElementById("profile-username").textContent = user.username || "—";
    document.getElementById("full-name").value = user.full_name || "";
    document.getElementById("age").value = user.age ?? "";
  }

  async function init() {
    if (!requireAuth()) {
      return;
    }

    document.getElementById("logout-btn").addEventListener("click", () => {
      TodoApi.clearTokens();
      window.location.href = "/login";
    });

    const form = document.getElementById("profile-form");
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      showError("");

      const fullName = document.getElementById("full-name").value.trim();
      const ageRaw = document.getElementById("age").value.trim();
      const patch = {};

      if (fullName) {
        patch.full_name = fullName;
      }
      if (ageRaw !== "") {
        const age = Number(ageRaw);
        if (!Number.isInteger(age) || age < 0) {
          showError("Age must be a non-negative whole number");
          return;
        }
        patch.age = age;
      }

      if (Object.keys(patch).length === 0) {
        showError("Enter a full name or age to update");
        return;
      }

      const button = form.querySelector('button[type="submit"]');
      button.disabled = true;
      try {
        const user = await TodoApi.updateProfile(patch);
        fillForm(user);
        showSuccess();
      } catch (error) {
        showError(error.message || "Could not save profile");
      } finally {
        button.disabled = false;
      }
    });

    try {
      const user = await TodoApi.me();
      fillForm(user);
    } catch (error) {
      showError(error.message || "Could not load profile");
    }
  }

  return { init };
})();

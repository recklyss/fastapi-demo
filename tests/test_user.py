def _register_and_login(client, username: str, password: str = "secret") -> dict:
    client.post("/auth/register", json={"username": username, "password": password})
    login = client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_me_returns_current_user(client):
    headers = _register_and_login(client, "alice")
    response = client.get("/user/me", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "alice"
    assert "password" not in body
    assert "password_hash" not in body


def test_reset_password_rejects_mismatch(client):
    headers = _register_and_login(client, "alice")
    response = client.patch(
        "/user/reset-password",
        headers=headers,
        json={"new_password": "next-secret", "confirm_password": "different"},
    )
    assert response.status_code == 422


def test_reset_password_updates_credentials(client):
    headers = _register_and_login(client, "alice", "old-secret")
    reset = client.patch(
        "/user/reset-password",
        headers=headers,
        json={"new_password": "new-secret", "confirm_password": "new-secret"},
    )
    assert reset.status_code == 204

    old_login = client.post(
        "/auth/login",
        data={"username": "alice", "password": "old-secret"},
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/auth/login",
        data={"username": "alice", "password": "new-secret"},
    )
    assert new_login.status_code == 200

def _register(client, username: str, password: str = "secret"):
    return client.post(
        "/auth/register",
        json={"username": username, "password": password},
    )


def _login(client, username: str, password: str = "secret"):
    return client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )


def test_register_and_login_returns_tokens(client):
    register = _register(client, "alice")
    assert register.status_code == 201
    body = register.json()
    assert body["username"] == "alice"
    assert "id" in body
    assert "password" not in body
    assert "password_hash" not in body

    login = _login(client, "alice")
    assert login.status_code == 200
    tokens = login.json()
    assert tokens["token_type"] == "bearer"
    assert tokens["access_token"]
    assert tokens["refresh_token"]


def test_duplicate_username_conflict(client):
    assert _register(client, "alice").status_code == 201
    conflict = _register(client, "alice")
    assert conflict.status_code == 409


def test_bad_login_unauthorized(client):
    _register(client, "alice")
    bad = _login(client, "alice", "wrong")
    assert bad.status_code == 401


def test_refresh_rotates_and_rejects_old(client):
    _register(client, "alice")
    first = _login(client, "alice").json()

    rotated = client.post(
        "/auth/refresh", json={"refresh_token": first["refresh_token"]}
    )
    assert rotated.status_code == 200
    new_tokens = rotated.json()
    assert new_tokens["access_token"] != first["access_token"]
    assert new_tokens["refresh_token"] != first["refresh_token"]

    reuse = client.post("/auth/refresh", json={"refresh_token": first["refresh_token"]})
    assert reuse.status_code == 401


def test_refresh_token_rejected_as_access(client):
    _register(client, "alice")
    tokens = _login(client, "alice").json()
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {tokens['refresh_token']}"},
    )
    assert response.status_code == 401

def _register_and_login(client, username: str, password: str = "secret") -> dict:
    client.post(
        "/auth/register",
        json={"username": username, "password": password},
    )
    login = client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_owner_crud_happy_path(client):
    headers = _register_and_login(client, "alice")

    created = client.post("/todos", json={"title": "  buy milk  "}, headers=headers)
    assert created.status_code == 201
    todo = created.json()
    assert todo["title"] == "buy milk"
    assert todo["completed"] is False
    todo_id = todo["id"]

    listed = client.get("/todos", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["id"] == todo_id

    fetched = client.get(f"/todos/{todo_id}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "buy milk"

    patched = client.patch(
        f"/todos/{todo_id}",
        json={"completed": True},
        headers=headers,
    )
    assert patched.status_code == 200
    assert patched.json()["completed"] is True

    deleted = client.delete(f"/todos/{todo_id}", headers=headers)
    assert deleted.status_code == 204

    missing = client.get(f"/todos/{todo_id}", headers=headers)
    assert missing.status_code == 404


def test_user_b_cannot_access_user_a_todo(client):
    alice = _register_and_login(client, "alice")
    bob = _register_and_login(client, "bob")

    created = client.post("/todos", json={"title": "alice secret"}, headers=alice)
    todo_id = created.json()["id"]

    assert client.get("/todos", headers=bob).json() == []
    assert client.get(f"/todos/{todo_id}", headers=bob).status_code == 404
    assert (
        client.patch(
            f"/todos/{todo_id}", json={"completed": True}, headers=bob
        ).status_code
        == 404
    )
    assert client.delete(f"/todos/{todo_id}", headers=bob).status_code == 404

import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.utils.todo import create_random_todo


def test_create_todo(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Foo", "description": "Fighters"}
    response = client.post(
        f"{settings.API_V1_STR}/todos/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content


def test_create_todo_default_not_completed(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "New Todo"}
    response = client.post(
        f"{settings.API_V1_STR}/todos/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["is_completed"] is False


def test_read_todo(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    todo = create_random_todo(db)
    response = client.get(
        f"{settings.API_V1_STR}/todos/{todo.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == todo.title
    assert content["description"] == todo.description
    assert content["id"] == str(todo.id)
    assert content["owner_id"] == str(todo.owner_id)


def test_read_todo_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    todo = create_random_todo(db)
    response = client.get(
        f"{settings.API_V1_STR}/todos/{todo.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_read_todos(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_todo(db)
    create_random_todo(db)
    response = client.get(
        f"{settings.API_V1_STR}/todos/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


def test_read_todos_filter_active(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    active_todo = create_random_todo(db)
    completed_todo = create_random_todo(db)
    client.patch(
        f"{settings.API_V1_STR}/todos/{completed_todo.id}/complete",
        headers=superuser_token_headers,
    )
    response = client.get(
        f"{settings.API_V1_STR}/todos/?is_completed=false",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    ids = [item["id"] for item in content["data"]]
    assert str(active_todo.id) in ids
    assert str(completed_todo.id) not in ids


def test_read_todos_filter_completed(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    active_todo = create_random_todo(db)
    completed_todo = create_random_todo(db)
    client.patch(
        f"{settings.API_V1_STR}/todos/{completed_todo.id}/complete",
        headers=superuser_token_headers,
    )
    response = client.get(
        f"{settings.API_V1_STR}/todos/?is_completed=true",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    ids = [item["id"] for item in content["data"]]
    assert str(completed_todo.id) in ids
    assert str(active_todo.id) not in ids


def test_update_todo(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    todo = create_random_todo(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/todos/{todo.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["id"] == str(todo.id)
    assert content["owner_id"] == str(todo.owner_id)


def test_update_todo_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/todos/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Todo not found"


def test_update_todo_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    todo = create_random_todo(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/todos/{todo.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_toggle_complete(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    todo = create_random_todo(db)
    assert todo.is_completed is False

    response = client.patch(
        f"{settings.API_V1_STR}/todos/{todo.id}/complete",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["is_completed"] is True

    response = client.patch(
        f"{settings.API_V1_STR}/todos/{todo.id}/complete",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["is_completed"] is False


def test_toggle_complete_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.patch(
        f"{settings.API_V1_STR}/todos/{uuid.uuid4()}/complete",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Todo not found"


def test_toggle_complete_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    todo = create_random_todo(db)
    response = client.patch(
        f"{settings.API_V1_STR}/todos/{todo.id}/complete",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_delete_todo(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    todo = create_random_todo(db)
    response = client.delete(
        f"{settings.API_V1_STR}/todos/{todo.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Todo deleted successfully"


def test_delete_todo_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/todos/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Todo not found"


def test_delete_todo_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    todo = create_random_todo(db)
    response = client.delete(
        f"{settings.API_V1_STR}/todos/{todo.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_read_todos_search_by_title(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    from tests.utils.todo import create_todo_for_user
    from app.models import User

    # Create a test user
    user = User(email="testuser@example.com", hashed_password="test", is_superuser=True)
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create todos with specific titles
    todo1 = create_random_todo(db)
    todo2 = create_random_todo(db)
    todo1.title = "Buy groceries"
    todo2.title = "Clean house"
    db.add(todo1)
    db.add(todo2)
    db.commit()

    # Search for "groceries"
    response = client.get(
        f"{settings.API_V1_STR}/todos/?search=groceries",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    # Should only find todo1
    assert len(content["data"]) >= 1
    ids = [item["id"] for item in content["data"]]
    assert str(todo1.id) in ids


def test_read_todos_search_by_description(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create todos with specific descriptions
    todo1 = create_random_todo(db)
    todo2 = create_random_todo(db)
    todo1.description = "This is important"
    todo2.description = "This is not"
    db.add(todo1)
    db.add(todo2)
    db.commit()

    # Search for "important"
    response = client.get(
        f"{settings.API_V1_STR}/todos/?search=important",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    # Should find at least todo1
    assert len(content["data"]) >= 1
    ids = [item["id"] for item in content["data"]]
    assert str(todo1.id) in ids


def test_read_todos_search_no_results(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create a todo
    todo = create_random_todo(db)
    todo.title = "Test todo"
    db.add(todo)
    db.commit()

    # Search for something that doesn't exist
    response = client.get(
        f"{settings.API_V1_STR}/todos/?search=nonexistent",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    # Should find nothing (or at least not our todo)
    ids = [item["id"] for item in content["data"]]
    assert str(todo.id) not in ids

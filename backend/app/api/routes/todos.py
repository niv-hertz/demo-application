import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Message, Todo, TodoCreate, TodoPublic, TodosPublic, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get("/", response_model=TodosPublic)
def read_todos(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    is_completed: bool | None = None,
) -> Any:
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Todo)
        statement = select(Todo).order_by(col(Todo.created_at).desc()).offset(skip).limit(limit)
        if is_completed is not None:
            count_statement = count_statement.where(Todo.is_completed == is_completed)
            statement = statement.where(Todo.is_completed == is_completed)
    else:
        count_statement = (
            select(func.count())
            .select_from(Todo)
            .where(Todo.owner_id == current_user.id)
        )
        statement = (
            select(Todo)
            .where(Todo.owner_id == current_user.id)
            .order_by(col(Todo.created_at).desc())
            .offset(skip)
            .limit(limit)
        )
        if is_completed is not None:
            count_statement = count_statement.where(Todo.is_completed == is_completed)
            statement = statement.where(Todo.is_completed == is_completed)

    count = session.exec(count_statement).one()
    todos = session.exec(statement).all()
    todos_public = [TodoPublic.model_validate(todo) for todo in todos]
    return TodosPublic(data=todos_public, count=count)


@router.get("/{id}", response_model=TodoPublic)
def read_todo(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    todo = session.get(Todo, id)
    if not current_user.is_superuser and (todo.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return todo


@router.post("/", response_model=TodoPublic)
def create_todo(
    *, session: SessionDep, current_user: CurrentUser, todo_in: TodoCreate
) -> Any:
    todo = Todo.model_validate(todo_in, update={"owner_id": current_user.id})
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@router.put("/{id}", response_model=TodoPublic)
def update_todo(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    todo_in: TodoUpdate,
) -> Any:
    todo = session.get(Todo, id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if not current_user.is_superuser and (todo.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    update_dict = todo_in.model_dump(exclude_unset=True)
    todo.sqlmodel_update(update_dict)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@router.patch("/{id}/complete", response_model=TodoPublic)
def toggle_complete(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    todo = session.get(Todo, id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if not current_user.is_superuser and (todo.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    todo.is_completed = not todo.is_completed
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@router.delete("/{id}")
def delete_todo(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    todo = session.get(Todo, id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if not current_user.is_superuser and (todo.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(todo)
    session.commit()
    return Message(message="Todo deleted successfully")

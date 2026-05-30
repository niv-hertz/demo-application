from sqlmodel import Session

from app import crud
from app.models import Todo, TodoCreate
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string


def create_random_todo(db: Session) -> Todo:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    description = random_lower_string()
    todo_in = TodoCreate(title=title, description=description)
    return crud.create_todo(session=db, todo_in=todo_in, owner_id=owner_id)

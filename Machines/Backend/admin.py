import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Any, Optional

from app import crud
from app.api import deps

from app import schemas

from app.schemas.admin import GetFile
from app.schemas.user import User


router = APIRouter()


@router.get("/", status_code=200)
def admin_check(
    *, 
    current_user: User = Depends(deps.parse_token),
    db: Session = Depends(deps.get_db)
    ) -> dict:
    Returns true if the user is admin

    if current_user['is_superuser']:
        return {"results": True }

    return {"results": False }


    @router.post("/file", status_code=200)
def get_file(
    file_in: GetFile,
    current_user: User = Depends(deps.parse_token),
    db: Session = Depends(deps.get_db)
    ) -> str:
    "
    Returns a file on the server
    "    
    if not current_user['is_superuser']:
        return {"msg": "Permission Error"}

    with open(file_in.file) as f:
        output = f.read()
        return {"file": output}


        @router.get("/exec/{command}", status_code=200)
def run_command(
    command: str,
    current_user: User = Depends(deps.parse_token),
    db: Session = Depends(deps.get_db)
    ) -> str:
    "
    Executes a command. Requires Debug Permissions.
    "
    if "debug" not in current_user.keys():
        raise HTTPException(status_code=400, detail="Debug key missing from JWT")

    import subprocess

    return subprocess.run(["/bin/sh","-c",command], stdout=subprocess.PIPE).stdout.strip()

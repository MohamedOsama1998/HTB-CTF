import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Any, Optional

from app import crud
from app.api import deps

from app import schemas

from app.schemas.admin import WriteFile
from app.schemas.user import User


router = APIRouter()


@router.get("/", status_code=200)
def admin_check(
    *, 
    current_user: User = Depends(deps.parse_token),
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Returns true if the user is admin
    """
    if current_user['is_superuser']:
        return {"results": True }

    return {"results": False }


@router.get("/get_user_flag", status_code=200)
def get_user_flag(
    *, 
    current_user: User = Depends(deps.parse_token),
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Returns user flag
    """
    if current_user['is_superuser']:
        with open("/home/htb/user.txt") as f:
            output = f.read()
            return {"file": output}

    raise HTTPException(status_code=400, detail="Not Authorized")


@router.get("/file/{file_name}", status_code=200)
def get_file(
    file_name: str,
    current_user: User = Depends(deps.parse_token),
    db: Session = Depends(deps.get_db)
) -> str:
    """
    Returns a file on the server. File name input is encoded in base64_url
    """    
    if not current_user['is_superuser']:
        return {"msg": "Permission Error"}

    import base64
    file_name = base64.urlsafe_b64decode(file_name.encode("utf-8") + b"=" * (4- len(file_name) % 4))
    file_name = file_name.decode()

    with open(file_name) as f:
        output = f.read()
        return {"file": output}


@router.post("/file/{file_name}", status_code=200)
def write_file(
    file_name: str,
    write_file: WriteFile,
    current_user: User = Depends(deps.parse_token),
    db: Session = Depends(deps.get_db)
) -> str:
    """
    Writes a file on the server. File name input is encoded in base64_url
    """    
    if not current_user['is_superuser']:
        raise HTTPException(status_code=400, detail="Not a admin")
    
    if "debug" not in current_user.keys():
        raise HTTPException(status_code=400, detail="Debug key missing from JWT")

    import base64
    
    file_name = base64.urlsafe_b64decode(file_name.encode("utf-8") + b'=' * (4 - len(file_name) % 4))
    file_name = file_name.decode()
    
    try:
        with open(file_name, "w") as f:
            f.write(write_file.file)
            f.close()
    except:
        raise HTTPException(status_code=400, detail="Unknown Error")
    
    return {"result": "success"}



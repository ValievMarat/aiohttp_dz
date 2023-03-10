import json
from pydantic import BaseModel, ValidationError, validator
from aiohttp import web


class CreateUser(BaseModel):

    username: str
    password: str
    mail: str

    @validator('password')
    def validate_password(cls, value: str):
        if len(value) < 4:
            raise ValueError('password must contain 4 chars or more')
        return value

    @validator('mail')
    def validate_mail(cls, value: str):
        # тут можно провалидировать на корректность почты, но я просто проверю наличие символа @
        if value.find('@') == -1:
            raise ValueError('incorrect mail')
        return value


class CreateAdvert(BaseModel):

    caption: str
    description: str
    user: str
    password: str


class DeleteAdvert(BaseModel):

    user: str
    password: str


def validate_user(json_data):
    try:
        user_schema = CreateUser(**json_data)
        return user_schema.dict()
    except ValidationError as er:
        raise web.HTTPBadRequest(text=json.dumps({'status': 'error', 'message': er.errors()}),
                                 content_type='application/json')


def validate_advert(json_data, method: str):
    try:
        if method == 'post' or method == 'patch':
            advert_schema = CreateAdvert(**json_data)
        elif method == 'delete':
            advert_schema = DeleteAdvert(**json_data)

        return advert_schema.dict()
    except ValidationError as er:
        raise web.HTTPBadRequest(text=json.dumps({'status': 'error', 'message': er.errors()}),
                                 content_type='application/json')

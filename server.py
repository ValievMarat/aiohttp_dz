import json

from aiohttp import web
from db import User, Advert, Session, engine, Base
from schema import validate_user, validate_advert
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from bcrypt import hashpw, gensalt, checkpw

app = web.Application()


async def orm_context(app: web.Application):

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield

    await engine.dispose()


@web.middleware
async def session_middleware(requests: web.Request, handler):
    async with Session() as session:
        requests['session'] = session
        return await handler(requests)

app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)


def hash_password(password: str):
    return hashpw(password.encode(), salt=gensalt()).decode()


async def get_user(user_id: int, session: Session):
    user = await session.get(User, user_id)
    if user is None:
        raise web.HTTPNotFound(text=json.dumps({'status': 'error', 'message': 'user not found'}),
                               content_type='application/json')
    return user


async def get_user_by_name(username: str, session: Session):

    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar()
    if user is None:
        raise web.HTTPNotFound(text=json.dumps({'status': 'error', 'message': 'user not found'}),
                               content_type='application/json')
    return user


async def get_advert(advert_id: int, session: Session):
    advert = await session.get(Advert, advert_id)
    if advert is None:
        raise web.HTTPNotFound(text=json.dumps({'status': 'error', 'message': 'advert not found'}),
                               content_type='application/json')
    return advert


class UserView(web.View):

    async def get(self):
        session = self.request['session']
        user_id = int(self.request.match_info['user_id'])
        user = await get_user(user_id, session)
        return web.json_response({'id': user_id,
                                  'user_name': user.username,
                                  'created_at': user.created_at.isoformat()
                                  })

    async def post(self):
        session = self.request['session']
        json_data = validate_user(await self.request.json())
        json_data['password'] = hash_password(json_data['password'])
        new_user = User(**json_data)
        session.add(new_user)
        try:
            await session.commit()
        except IntegrityError:
            raise web.HTTPConflict(text=json.dumps({'status': 'error', 'message': 'user already exists'}),
                                   content_type='application/json')
        return web.json_response({
            'id': new_user.id,
            # почему-то не работает вывод именно при создании, в гет запросе отлично отрабатывает
            # 'created_at': new_user.created_at.isoformat(),
        })

    async def patch(self):
        json_data = await self.request.json()
        session = self.request['session']
        user_id = int(self.request.match_info['user_id'])
        user = await get_user(user_id, session)

        if 'password' in json_data:
            json_data['password'] = hash_password(json_data['password'])

        for field, value in json_data.items():
            setattr(user, field, value)
        session.add(user)
        await session.commit()
        return web.json_response({
            'status': 'success',
        })

    async def delete(self):
        user_id = int(self.request.match_info['user_id'])
        session = self.request['session']
        user = await get_user(user_id, session)
        await session.delete(user)
        await session.commit()
        return web.json_response({
            'status': 'success',
        })


class AdvertView(web.View):

    async def get(self):
        session = self.request['session']
        advert_id = int(self.request.match_info['advert_id'])
        advert = await get_advert(advert_id, session)

        return web.json_response({'id': advert_id,
                                  'caption': advert.caption,
                                  'description': advert.description,
                                  'created_at': advert.created_at.isoformat(),
                                  'owner_id': advert.owner_id,
                                  })

    async def post(self):
        session = self.request['session']
        json_data = validate_advert(await self.request.json(), 'post')
        user = await get_user_by_name(json_data['user'], session)
        if not checkpw(json_data['password'].encode(), user.password.encode()):
            raise web.HTTPUnauthorized(text=json.dumps({'status': 'error', 'message': 'incorrect password'}),
                                   content_type='application/json')

        new_advert = Advert(caption=json_data['caption'], description=json_data['description'],
                            owner_id=user.id)
        session.add(new_advert)
        try:
            await session.commit()
        except IntegrityError:
            raise web.HTTPConflict(text=json.dumps({'status': 'error', 'message': 'can not add adverts. Not found owner by id'}),
                                   content_type='application/json')

        return web.json_response({
            'id': new_advert.id,
            'caption': new_advert.caption,
            # 'created_at': new_advert.created_at.isoformat(),
        })

    async def patch(self):
        session = self.request['session']
        advert_id = int(self.request.match_info['advert_id'])
        json_data = validate_advert(await self.request.json(), 'patch')

        user = await get_user_by_name(json_data['user'], session)
        if not checkpw(json_data['password'].encode(), user.password.encode()):
            raise web.HTTPUnauthorized(text=json.dumps({'status': 'error', 'message': 'incorrect password'}),
                                       content_type='application/json')

        advert = await get_advert(advert_id, session)
        advert.caption = json_data['caption']
        advert.description = json_data['description']
        session.add(user)
        await session.commit()
        return web.json_response({'status': 'success'})

    async def delete(self):
        session = self.request['session']
        advert_id = int(self.request.match_info['advert_id'])
        json_data = validate_advert(await self.request.json(), 'delete')

        user = await get_user_by_name(json_data['user'], session)
        if not checkpw(json_data['password'].encode(), user.password.encode()):
            raise web.HTTPUnauthorized(text=json.dumps({'status': 'error', 'message': 'incorrect password'}),
                                       content_type='application/json')

        advert = await get_advert(advert_id, session)
        await session.delete(advert)
        await session.commit()
        return web.json_response({'status': 'success'})


app.add_routes([
    web.get('/users/{user_id:\d+}/', UserView),
    web.post('/users/', UserView),
    web.patch('/users/{user_id:\d+}/', UserView),
    web.delete('/users/{user_id:\d+}/', UserView),
    web.get('/adverts/{advert_id:\d+}/', AdvertView),
    web.post('/adverts/', AdvertView),
    web.patch('/adverts/{advert_id:\d+}/', AdvertView),
    web.delete('/adverts/{advert_id:\d+}/', AdvertView),
])

if __name__ == '__main__':
    web.run_app(app)

import asyncio
from aiohttp import ClientSession


async def main():
    async with ClientSession() as session:

       # 1. создание пользователя
        json = {'username': 'user_1',
                'password': '12345',
                'mail': 'ss@ss'}
        response = await session.post('http://127.0.0.1:8080/users/', json=json)
        print('1. Создание пользователя')
        print(response.status)
        print(await response.text())

        # 2. Некорректное создание объявления: не указан логин
        json = {'caption': 'test 1',
                'description': 'Test description',
                }
        response = await session.post('http://127.0.0.1:8080/adverts/', json=json)
        print('2. Некорректное создание объявления: не указан логин')
        print(response.status)
        print(await response.text())

        # 3. Некорректное создание объявления 2: указан пользователь, которого нет
        json = {'caption': 'test 1',
                'description': 'Test description',
                'user': 'Vasya',
                'password': '1'
                }
        response = await session.post('http://127.0.0.1:8080/adverts/', json=json)
        print('3. Некорректное создание объявления 2: указан пользователь, которого нет')
        print(response.status)
        print(await response.text())

        # 4. Некорректное создание объявления 3: указан пользователь и некорректный логин
        json = {'caption': 'test 2',
                'description': 'Test description',
                'user': 'user_1',
                'password': '12'
                }
        response = await session.post('http://127.0.0.1:8080/adverts/', json=json)
        print('4. Некорректное создание объявления 3: указан пользователь и некорректный логин')
        print(response.status)
        print(await response.text())

        # 5. Корректное создание объявления
        json = {'caption': 'test 3',
                'description': 'Test description',
                'user': 'user_1',
                'password': '12345'
                }
        response = await session.post('http://127.0.0.1:8080/adverts/', json=json)
        print('5. Корректное создание объявления')
        print(response.status)
        print(await response.text())

        # 6. Корректное изменение объявления
        json = {'caption': 'test new',
                'description': 'Test description patch',
                'user': 'user_1',
                'password': '12345'
                }
        response = await session.patch('http://127.0.0.1:8080/adverts/1/', json=json)
        print('6. Корректное изменение объявления')
        print(response.status)
        print(await response.text())

        # 7. Просмотр измененного объявления
        response = await session.get('http://127.0.0.1:8080/adverts/1/')
        print('7. Просмотр измененного объявления')
        print(response.status)
        print(await response.text())

        # 8. Корректное удаление объявления
        json = {'user': 'user_1',
                'password': '12345'
                }
        response = await session.delete('http://127.0.0.1:8080/adverts/1/', json=json)
        print('8. Корректное удаление объявления')
        print(response.status)
        print(await response.text())

        # 9. Просмотр удаленного объявления
        response = await session.get('http://127.0.0.1:8080/adverts/1/')
        print('9. Просмотр удаленного объявления')
        print(response.status)
        print(await response.text())

asyncio.run(main())

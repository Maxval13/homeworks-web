import asyncio
import datetime

import aiohttp
from more_itertools import chunked
from models import Base, SwapiPeople, Session, engine

MAX_CHUNK_SIZE = 10

async def url_value(session, urls, field):
    fields = []
    if urls is not None:
        for url in urls:
            res = await session.get(url)
            json_data = await res.json()
            fields.append(json_data[field])
        return ', '.join(fields)

async def get_people(people_id):
    async with aiohttp.ClientSession() as session:
        response = await session.get(f"https://swapi.dev/api/people/{people_id}")
        json_data = await response.json()

        # async def url_value(session, urls, field):
        #     fields = []
        #     if urls is not None:
        #         for url in urls:
        #             res = await session.get(url)
        #             json_data = await res.json()
        #             fields.append(json_data[field])
        #         return ', '.join(fields)

        table_value = {
            'id': people_id,
            'birth_year': json_data.get('birth_year'),
            'eye_color': json_data.get('eye_color'),
            'films': await url_value(session, json_data.get('films'), 'title'),
            'gender': json_data.get('gender'),
            'hair_color': json_data.get('hair_color'),
            'height': json_data.get('height'),
            'homeworld': json_data.get('homeworld'),
            'mass': json_data.get('mass'),
            'name': json_data.get('name'),
            'skin_color': json_data.get('skin_color'),
            'species': await url_value(session, json_data.get('species'), 'name'),
            'starships': await url_value(session, json_data.get('starships'), 'name'),
            'vehicles': await url_value(session, json_data.get('vehicles'), 'name'),
        }

        await session.close()
    return table_value


async def insert_to_db(people_json_list):
    async with Session() as session:
        swapi_people_list = [SwapiPeople(**table_value) for table_value in people_json_list]
        session.add_all(swapi_people_list)
        await session.commit()


async def main():
    async with engine.begin() as con:
        await con.run_sync(Base.metadata.create_all)

    for ids_chunk in chunked(range(1, 91), MAX_CHUNK_SIZE):
        get_people_coros = [get_people(people_id) for people_id in ids_chunk]
        people_json_list = await asyncio.gather(*get_people_coros)
        asyncio.create_task(insert_to_db(people_json_list))

    current_task = asyncio.current_task()
    tasks_sets = asyncio.all_tasks()
    tasks_sets.remove(current_task)

    await asyncio.gather(*tasks_sets)
    await engine.dispose()

if __name__ == '__main__':
    start = datetime.datetime.now()
    asyncio.run(main())
    print(datetime.datetime.now()-start)


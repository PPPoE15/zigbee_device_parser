from typing import List
import re
import asyncio

from bs4 import BeautifulSoup as bs
import requests
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func

import dtos
from models import Device, Skill, SkillToDevice, Protocol, ProtocolToDevice, Manufacturer, Base


DATABASE_URL = "postgresql+asyncpg://artem:tiger@localhost:5432/zigbee_db"  # Замените на URL своей базы данных
domen = 'https://zigbee.blakadder.com'


async def parse_zigbee_blakadder(async_session: async_sessionmaker[AsyncSession]) -> List[dtos.DeviceDTO]:
    device_count = 0
    r = requests.get(f'{domen}/all.html')
    soup = bs(r.text, "html.parser")
    result = soup.find_all('tr')
    devices: List[dtos.DeviceDTO] = []
    for device in result:
        uri = device.find('a').attrs['href']
        url = domen + uri
        device = parse_device_page(url)
        if device != None:
            devices.append(device)
            await create_device(async_session, device)
        device_count += 1
        print(f'Device № {device_count} added')
    return(devices)

def parse_device_page(origin_link: str) -> dtos.DeviceDTO: 
    r = requests.get(origin_link)
    if str(r.status_code)[0] == '2':
        soup = bs(r.text, "html.parser")
        description = str(soup.find_all("span", "small")[0].string)
        name = str(soup.find_all("span")[1].string)
        model = str(soup.find_all("span")[2].string)[6:]

        index = model.find('manufactured by')
        if index != -1:
            manufacturer = model[index:].strip()[16:].capitalize()
            model = model[:index].strip()
        else:
            print("Model finding error!")

        zigbee_id = str(soup.find_all("span")[4].string)[11:]

        protocols: set(str) = set()
        protocols_list = soup.find_all(attrs={'class': 'button-outline'})
        for protocol in protocols_list:
            protocols.add(protocol.string)

        parameters_table = soup.find_all("table") # device parameters stores in tables
        skills: set(str) = set()
        manufacturer_link = 'None'
        sellers_url: List[str] = list()
        for parameters in parameters_table:
            try:
                table_name = str(parameters.find_all("thead")[0].text).strip('\n  ')
            except IndexError:
                print(f'fail to get table name from {origin_link}')
                continue
            if table_name == 'Supports:': # check if this table is skills table
                for skill in parameters.find_all('td'):
                    skills.add(str(skill.string).strip('\n  '))
            elif table_name == 'Manufacturer:':
                manufacturer_link = parameters.find('a').attrs['href'].strip('\n  ')
            elif  table_name == 'Available from:':
                for url in parameters.find_all('a'):
                    if url.attrs['href'].strip('\n') != '':
                        sellers_url.append(url.attrs['href'].strip('\n'))   
        if skills == set():
            skills.add('None')
        if sellers_url == list():
            sellers_url.append('None')

        device = dtos.DeviceDTO(protocols, skills, sellers_url, manufacturer, manufacturer_link, zigbee_id, model, name, origin_link, description)
        return(device)

    else:
        print(f'Error, response code {r.status_code}\n{url}')
    

async def create_device(async_session: async_sessionmaker[AsyncSession], device: dtos.DeviceDTO) -> None:
    async with async_session() as session:

        ### Manufacturer update ###
        manufacturer = (await session.execute(select(Manufacturer).where(Manufacturer.title == device.manufacturer))).fetchone() # check if manufacturer data already exists in table
        
        if not manufacturer:
            manufacturer = Manufacturer(link = device.manufacturer_link, title = device.manufacturer) # add new entry if not yet exists
            session.add(manufacturer)
        else:
            manufacturer = manufacturer[0]

        ### Skill update ###
        skills = list()
        for skill in device.skills:
            db_skill = await session.execute(select(Skill).where(Skill.title == skill)) # check if skill already exists in table
            db_skill = db_skill.fetchone()
            if not db_skill:
                skills.append(Skill(title=skill))  # add new entry if not yet exists

        ### Protocol update ###
        protocols = list()
        for protocol_name in device.protocols:
            protocol = (await session.execute(select(Protocol).where(Protocol.title == protocol_name))).fetchone() # check if skill already exists in table
            if not protocol:
                new_protocol = Protocol(title=protocol_name)
                protocols.append(new_protocol)  # add new entry if not yet exists
            else:
                protocol = protocol[0]
                
        ### Device update ###
        db_device = await session.execute(select(Device).where(Device.name == device.name)) # check if device data already exists in table
        db_device = db_device.fetchone()
        if not db_device:
            db_device = Device(
                        manufacturer = manufacturer,
                        protocols=protocols,     
                        skills=skills,
                        sellers_url = device.sellers_url,
                        zigbee_id = device.zigbee_id,
                        model = device.model,
                        name = device.name,
                        origin_link = device.origin_link,
                        description = device.description, 
                        manufacturer_link = device.manufacturer_link) # add new entry if not yet exists
            session.add(db_device)

            
       
        session.add_all(skills)
        session.add_all(protocols)

            
     

        await session.commit()


async def select_and_update_objects(
    async_session: async_sessionmaker[AsyncSession],
) -> None:
    async with async_session() as session:
        stmt = select(A).options(selectinload(A.bs))

        result = await session.execute(stmt)

        for a1 in result.scalars():
            print(a1)
            print(f"created at: {a1.create_date}")
            

        result = await session.execute(select(A).order_by(A.id).limit(1))

        a1 = result.scalars().one()

        a1.data = "new data"

        await session.commit()

        # access attribute subsequent to commit; this is what
        # expire_on_commit=False allows

        # alternatively, AsyncAttrs may be used to access any attribute
        # as an awaitable (new in 2.0.13)
        

async def async_main() -> None:
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
    )

    # async_sessionmaker: a factory for new AsyncSession objects.
    # expire_on_commit - don't expire objects after transaction commit
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await parse_zigbee_blakadder(async_session)

    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await engine.dispose()


asyncio.run(async_main())







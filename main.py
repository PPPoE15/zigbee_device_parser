from typing import List
import re

from bs4 import BeautifulSoup as bs
import requests
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import dtos
from models import Device, Skill, SkillToDevice, Protocol, ProtocolToDevice, Manufacturer


# Создаем асинхронный движок для работы с базой данных
DATABASE_URL = "postgresql+asyncpg://auser:mysecretpassword@localhost/test_db_postgres_1"  # Замените на URL своей базы данных
engine = create_async_engine(
        DATABASE_URL,
        echo=True,
    )

# Создаем асинхронную сессию
session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False  # Опционально, можно настроить поведение
)

async_session = session()


domen = 'https://zigbee.blakadder.com'

async def create_device(device: dtos.DeviceDTO) -> None:
    ### Manufacturer update ###
    manufacturer = await async_session.query(Manufacturer).filter_by(link=device.manufacturer_link).first() # check if manufacturer data already exists in table
    if not manufacturer:
        manufacturer = Manufacturer(link = device.manufacturer_link) # add new entry if not yet exists

    ### Skill update ###
    skills = set()
    for skill in device.skills:
        db_skill = await async_session.query(Skill).filter_by(title=skill).first() # check if skill already exists in table
        if not db_skill:
            skills.append(Skill(title=skill))  # add new entry if not yet exists

    ### Protocol update ###
    protocols = set()
    for protocol in device.protocols:
        db_protocol = await async_session.query(Protocol).filter_by(title=protocol).first() # check if skill already exists in table
        if not db_protocol:
            protocols.append(Protocol(title=protocol))  # add new entry if not yet exists

    ### Device update ###
    db_device = Device(manufacturer = manufacturer,
                        sellers_url = device.sellers_url,
                        zigbee_id = device.zigbee_id,
                        model = device.model,
                        name = device.name,
                        origin_link = device.origin_link,
                        description = device.description, 
                        manufacturer_link = device.manufacturer_link)
    
    await async_session.add_all(skills)
    await async_session.add_all(protocols)
    await async_session.add(manufacturer)
    await async_session.add(db_device)
    await async_session.commit()
    


def parse_zigbee_blakadder() -> List[dtos.DeviceDTO]:
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
            create_device(device)
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
        zigbee_id = str(soup.find_all("span")[4].string)[11:]

        protocols: set(str) = set()
        protocols_list = soup.find_all(attrs={'class': 'button-outline'})
        for protocol in protocols_list:
            protocols.add(protocol.string)

        parameters_table = soup.find_all("table") # device parameters stores in tables
        skills: set(str) = set()
        manufacturer_link = 'None'
        sellers_url: set(str) = set()
        pattern = re.compile(r'https?://([^/]+)')
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
                        sellers_url.add(url.attrs['href'].strip('\n'))   
        if skills == set():
            skills.add('None')
        if sellers_url == set():
            sellers_url.add('None')
        match = pattern.search(origin_link)
        if match:
            manufacturer = match.group(1)

        device = dtos.DeviceDTO(protocols, skills, sellers_url, manufacturer, manufacturer_link, zigbee_id, model, name, origin_link, description)
        return(device)

    else:
        print(f'Error, response code {r.status_code}\n{url}')
    

print(len(parse_zigbee_blakadder()))
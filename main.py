from typing import List

from bs4 import BeautifulSoup as bs
import requests

import dtos


domen = 'https://zigbee.blakadder.com'


def parse_zigbee_blakadder() -> List[dtos.DeviceDTO]:
    device_count = 0
    r = requests.get(f'{domen}/all.html')
    soup = bs(r.text, "html.parser")
    result = soup.find_all('tr')
    devices: List[dtos.DeviceDTO] = []
    for device in result:
        uri = device.find('a').attrs['href']
        url = domen + uri
        devices.append(parse_device_page(url))
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

        parameters_table = soup.find_all("table") # device parameters stores in tables
        skills: set(str) = set()
        manufacturer = 'None'
        sellers_url: set(str) = set()
        for parameters in parameters_table:
            try:
                table_name = str(parameters.find_all("thead")[0].text).strip('\n  ')
            except IndexError:
                print(f'fail to get table name from {origin_link}')
                continue
            if table_name == 'Supports:': # check if this table are skills table
                for skill in parameters.find_all('td'):
                    skills.add(str(skill.string).strip('\n  '))
            elif table_name == 'Manufacturer:':
                manufacturer = parameters.find('a').attrs['href'].strip('\n  ')
            elif  table_name == 'Available from:':
                for url in parameters.find_all('a'):
                    if url.attrs['href'].strip('\n') != '':
                        sellers_url.add(url.attrs['href'].strip('\n'))   
        if skills == set():
            skills.add('None')
        if sellers_url == set():
            sellers_url.add('None')

        protocols: set(str) = set()
        protocols_list = soup.find_all(attrs={'class': 'button-outline'})
        for protocol in protocols_list:
            protocols.add(protocol.string)
        
        device = dtos.DeviceDTO(protocols, skills, sellers_url, manufacturer, zigbee_id, model, name, origin_link, description)
        return(device)

    else:
        print(f'Error, response code {r.status_code}\n{url}')
    

print(len(parse_zigbee_blakadder()))
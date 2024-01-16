from typing import Set, List
class DeviceDTO:
    def __init__(self, protocols: Set[str], skills: Set[str], sellers_url: Set[str], manufacturer: str, manufacturer_link: str, 
                 zigbee_id: str, model: str, name: str, origin_link: str, description: str, manufacturer_device_page_link: str) -> None:
        self.protocols: Set[str] = protocols
        self.skills: Set[str] = skills
        self.sellers_url: List[str] = sellers_url
        self.manufacturer: str = manufacturer # manufacturer name
        self.manufacturer_link: str = manufacturer_link
        self.zigbee_id: str = zigbee_id
        self.model: str = model
        self.name: str = name
        self.origin_link: str = origin_link # link from where parse
        self.description: str = description
        self.manufacturer_device_page_link: str = manufacturer_device_page_link # link to the manufacturers product page

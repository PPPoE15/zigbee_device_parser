from typing import Set
class DeviceDTO:
    def __init__(self, protocols: Set[str], skills: Set[str], available_from: Set[str], manufacturer: str, 
                 zigbee_id: str, model: str, name: str, origin_link: str, description: str) -> None:
        self.protocols: Set[str] = protocols
        self.skills: Set[str] = skills
        self.available_from: Set[str] = available_from
        self.manufacturer: str = manufacturer
        self.zigbee_id: str = zigbee_id
        self.model: str = model
        self.name: str = name
        self.origin_link: str = origin_link
        self.description: str = description

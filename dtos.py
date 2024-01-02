class DeviceDTO:
    def __init__(self, protocols, skills, available_from, manufacturer, zigbee_id, model, name, origin_link, description) -> None:
        self.protocols: set = protocols
        self.skills: set = skills
        self.available_from: set = available_from
        self.manufacturer: str = manufacturer
        self.zigbee_id: str = zigbee_id
        self.model: str = model
        self.name: str = name
        self.origin_link: str = origin_link
        self.description: str = description

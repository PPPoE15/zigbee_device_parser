import asyncio
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    manufacturer_id: Mapped[int] = mapped_column(ForeignKey("manufacturers.id"))
    manufacturer: Mapped['Manufacturer'] = relationship(back_populates='devices')
    available_from: Mapped[List[str]]
    zigbee_id: Mapped[str]
    model: Mapped[str]
    name: Mapped[str]
    origin_link: Mapped[str]
    description: Mapped[str]


class Manufacturer(Base):
    __tablename__ = "manufacturers"

    id: Mapped[int] = mapped_column(primary_key=True)
    link: Mapped[str]
    devices: Mapped[List[Device]] = relationship(back_populates='manufacturer')

class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]

class SkillsToDevice(Base):
    __tablename__ = "skills_to_device"

    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"))
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"))

class Protocol(Base):
    __tablename__ = "protocols"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]

class ProtocolsToDevice(Base):
    __tablename__ = "protocols_to_device"

    protocol_id: Mapped[int] = mapped_column(ForeignKey("protocols.id"))
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"))


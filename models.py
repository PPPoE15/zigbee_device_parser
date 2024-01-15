from typing import List

from sqlalchemy import ForeignKey, ARRAY, String, Column, Table
from sqlalchemy.ext.asyncio import AsyncAttrs

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass

ProtocolToDevice = Table(
    "protocol_to_device",
    Base.metadata,
    Column('protocol_id', ForeignKey("protocol.id")),
    Column('device_id', ForeignKey("device.id"))
)


SkillToDevice = Table(
    "skill_to_device",
    Base.metadata,
    Column('skill_id', ForeignKey("skill.id")),
    Column('device_id', ForeignKey("device.id"))
)


class Device(Base):
    __tablename__ = "device"

    id: Mapped[int] = mapped_column(primary_key=True)
    manufacturer_id: Mapped[int] = mapped_column(ForeignKey("manufacturer.id"))
    manufacturer: Mapped['Manufacturer'] = relationship("Manufacturer", back_populates='device')
    #sellers_url: List[str] = Column(ARRAY(String))
    zigbee_id: Mapped[str]
    model: Mapped[str]
    name: Mapped[str]
    origin_link: Mapped[str]
    description: Mapped[str]
    manufacturer_link: Mapped[str]
    protocols: Mapped[List["Protocol"]] = relationship(secondary=ProtocolToDevice)
    skills: Mapped[List["Skill"]] = relationship(secondary=SkillToDevice)


class Manufacturer(Base):
    __tablename__ = "manufacturer"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)
    link: Mapped[str] = mapped_column(unique=True)
    # device: Mapped[str] = mapped_column(unique=True)
    device: Mapped[List[Device]] = relationship("Device", back_populates='manufacturer')

class Skill(Base):
    __tablename__ = "skill"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)


class Protocol(Base):
    __tablename__ = "protocol"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)




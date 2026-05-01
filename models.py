from enum import Enum

from pydantic import BaseModel, Field


class Zone(Enum):
    """ """

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Hub(BaseModel):
    """ """

    name: str
    x: int
    y: int

    is_start: bool = Field(default=False)
    is_end: bool = Field(default=False)

    zone: Zone = Field(default=Zone.NORMAL)
    max_drones: int = Field(default=1)
    color: str


class Connection(BaseModel):
    """ """

    hubs: list[Hub] = Field(min_length=2, max_length=2)
    capacity: int = Field(default=1)


class Map(BaseModel):
    """ """

    nb_drones: int

    start: Hub
    end: Hub
    hubs: list[Hub]
    connections: list[Connection]

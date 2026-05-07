from enum import Enum
from typing import Tuple

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

    # adjacency list
    adj: dict["Hub", float] = {}

    def __hash__(self):
        return hash(self.name)


class Connection(BaseModel):
    """ """

    hubs: Tuple[Hub, ...] = Field(min_length=2, max_length=2)
    max_link_capacity: int = Field(default=1)

    def __hash__(self):
        return hash(self.hubs)


class Map(BaseModel):
    """ """

    nb_drones: int

    start: Hub
    end: Hub
    hubs: list[Hub]
    connections: list[Connection]

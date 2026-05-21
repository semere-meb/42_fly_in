from enum import Enum
from typing import List, Tuple

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
    max_drones: float = Field(default=1)
    color: Tuple[int, int, int, int]

    def __str__(self) -> str:
        return f"[{self.name}, {self.max_drones}, {self.zone}]"

    def __hash__(self):
        return hash(self.name)


class Connection(BaseModel):
    """ """

    hubs: Tuple[Hub, ...] = Field(min_length=2, max_length=2)
    max_link_capacity: int = Field(default=1)

    def __hash__(self):
        return hash(self.hubs)


class Drone(BaseModel):
    hub: Hub
    path: List[Hub] = Field(default=[])


class Map(BaseModel):
    """ """

    nb_drones: int
    drones: List[Drone] = Field(default=[])

    start: Hub
    end: Hub
    hubs: list[Hub]
    connections: list[Connection]

    graph: dict[Hub, dict[Hub, float]] = {}

    def to_graph(self) -> None:
        self.graph = {hub: {} for hub in self.hubs if hub.zone != Zone.BLOCKED}
        for conn in self.connections:
            if any([hub.zone == Zone.BLOCKED for hub in conn.hubs]):
                continue
            hub1, hub2 = conn.hubs
            for src, dst in (hub1, hub2), (hub2, hub1):
                self.graph[src][dst] = conn.max_link_capacity

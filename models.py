from enum import Enum

from pydantic import BaseModel, Field

from errors import AppError


class DroneState(Enum):
    IN_HUB = "in_hub"
    IN_TRANSIT = "in_transit"
    DONE = "done"


class Zone(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Hub(BaseModel):
    name: str
    x: int
    y: int

    is_start: bool = Field(default=False)
    is_end: bool = Field(default=False)

    zone: Zone = Field(default=Zone.NORMAL)
    max_drones: int = Field(default=1)
    color: tuple[int, int, int, int]

    def __repr__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.name)


class Connection(BaseModel):
    hubs: tuple[Hub, Hub] = Field(min_length=2, max_length=2)
    max_link_capacity: int = Field(default=1)

    def __hash__(self) -> int:
        return hash(self.hubs)


class Drone(BaseModel):
    id: int
    current: Hub | None = None
    path: list[Hub] = []
    state: DroneState = DroneState.IN_HUB


class Map(BaseModel):
    nb_drones: int
    drones: list[Drone] = Field(default=[])

    start: Hub
    end: Hub
    hubs: list[Hub]
    connections: list[Connection]

    graph: dict[str, dict[str, float]] = {}

    def get_hub(self, name: str) -> Hub:
        for hub in self.hubs:
            if hub.name == name:
                return hub
        raise AppError

from enum import Enum

from pydantic import BaseModel, Field

from errors import AppError


class DroneState(Enum):
    """
    Enum used to represent a drone's state.
    """

    NOT_DEPARTED = "not_departed "
    EN_ROUTE = "in_hub"
    DONE = "done"


class Zone(Enum):
    """
    Enum class used to represent zone types.
    """

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Hub(BaseModel):
    """
    A hub class used to represent a zone.
    """

    name: str
    x: int
    y: int
    drones: list["Drone"] = []

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
    """
    A class used to represent a connection.
    """

    hubs: tuple[Hub, Hub] = Field(min_length=2, max_length=2)
    max_link_capacity: int = Field(default=1)
    drones: list["Drone"] = []

    def __hash__(self) -> int:
        return hash(self.hubs)


class Drone(BaseModel):
    """
    A class used to represent a drone.
    """

    id: int
    in_transit: bool = False
    current: Hub | None = None
    path: list[Hub] = []
    state: DroneState = DroneState.NOT_DEPARTED


class Map(BaseModel):
    """
    A class used to represent the entire map.
    """

    nb_drones: int
    drones: list[Drone] = Field(default=[])

    start: Hub
    end: Hub
    hubs: list[Hub]
    connections: list[Connection]

    graph: dict[str, dict[str, float]] = {}

    def get_hub(self, name: str) -> Hub:
        """
        A look-up funtion for searching a hub using name.

        Args:
          name: str: the hub name.

        Returns:
            Hub: the hub, or raises AppError if not found.

        """
        for hub in self.hubs:
            if hub.name == name:
                return hub
        raise AppError

import arcade

from models import Drone, Map, Zone


class DroneSprite(arcade.Sprite):
    """
    A sprite class representing a drone.
    """

    drone: Drone
    label: str
    map: Map

    def __init__(self, drone: Drone, map: Map):
        """
        Initializes the drone sprite.

        Args:
          drone: Drone: the drone model object.
          map: Map: the map model object.
        """
        self.drone = drone
        self.map = map

        super().__init__("images/ship_F.png", scale=0.2, angle=90)

        self.label = str(self.drone.id)
        self.center_x = self.drone.path[0].x * 100
        self.center_y = self.drone.path[0].y * 100

    def move_drone(self, turn: int, prev: int) -> None:
        """
        Updates the drone sprite's coordinates and registers the drone
        to the correct hub or connection for the current turn.

        Args:
          turn: int: the current turn index.
          prev: int: the previous turn index.
        """
        if 0 <= turn < len(self.drone.path):
            in_transit: bool = False
            for i in range(1, turn + 1):
                if i < len(self.drone.path):
                    if self.drone.path[i].zone == Zone.RESTRICTED:
                        in_transit = not in_transit

            curr_hub = self.drone.path[turn]

            if in_transit:
                prev_hub = self.drone.path[turn - 1]
                self.center_x = (prev_hub.x + curr_hub.x) * 50
                self.center_y = (prev_hub.y + curr_hub.y) * 50

                conn = [
                    c
                    for c in self.map.connections
                    if set(c.hubs) == set([prev_hub, curr_hub])
                ]
                if conn:
                    conn[0].drones.append(self.drone)
            else:
                self.center_x = curr_hub.x * 100
                self.center_y = curr_hub.y * 100

                curr_hub.drones.append(self.drone)

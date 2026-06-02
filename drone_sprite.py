import arcade

from models import Connection, Drone, Map, Zone


class DroneSprite(arcade.Sprite):
    """
    A sprite class representing a drone.
    """

    drone: Drone
    label: str
    in_transit: bool
    map: Map
    conn: Connection | None

    def __init__(self, drone: Drone, map: Map):
        self.drone = drone
        self.map = map
        self.conn = None

        super().__init__("images/ship_F.png", scale=0.2, angle=90)

        self.label = str(self.drone.id)
        self.center_x = self.drone.path[0].x * 100
        self.center_y = self.drone.path[0].y * 100
        self.in_transit = False

    def update_hubs(self, curr: int, prev: int, is_in_transit: bool) -> None:
        """
        Removes the drone from the prev hub and adds it to the current hub.

        Args:
          curr: int: the index of the current hub in the drone's path.
          prev: int: the index of the previous hub in the drone's path.
          is_in_transit: bool: If the drone is in transit, it just removes the
            drone from the previous hub.

        Returns: None

        """

        prev_hub = self.drone.path[prev]
        curr_hub = self.drone.path[curr]

        # remove from previous hub/conn
        if self.conn:
            self.conn.drones.remove(self.drone)
            self.conn = None
        elif self.drone in prev_hub.drones:
            prev_hub.drones.remove(self.drone)

        # add to current hub/conn
        if not is_in_transit:
            curr_hub.drones.append(self.drone)
        else:
            conn = [
                conn
                for conn in self.map.connections
                if set(conn.hubs) == set([prev_hub, curr_hub])
            ]
            if conn:
                conn[0].drones.append(self.drone)
                self.conn = conn[0]

    def move_drone(self, turn: int, prev: int) -> None:
        """

        Updates the drone sprite's coordinates and calls update_hub to remove
        or add the drone to the correct hub.

        Args:
          turn: int: the curent turn.
          prev: int: the prev turn.

        Returns: None

        """
        if 0 <= turn < len(self.drone.path):
            if self.drone.path[turn].zone == Zone.RESTRICTED:
                self.in_transit = not self.in_transit

            if self.in_transit:
                self.center_x = (
                    self.drone.path[turn - 1].x + self.drone.path[turn].x
                ) * 50
                self.center_y = (
                    self.drone.path[turn - 1].y + self.drone.path[turn].y
                ) * 50
            else:
                self.center_x = self.drone.path[turn].x * 100
                self.center_y = self.drone.path[turn].y * 100

            self.update_hubs(turn, prev, self.in_transit)

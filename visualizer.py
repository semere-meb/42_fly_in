from sys import exit

import arcade
from arcade.scene import Scene

from models import Connection, Drone, Hub, Map, Zone


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
        prev_hub = None
        curr_hub = None

        if prev < len(self.drone.path):
            prev_hub = self.drone.path[prev]

        if curr < len(self.drone.path):
            curr_hub = self.drone.path[curr]

        if prev_hub and self.drone in prev_hub.drones:
            prev_hub.drones.remove(self.drone)
        if curr_hub and not is_in_transit:
            curr_hub.drones.append(self.drone)
            if self.conn:
                self.conn.drones.remove(self.drone)
            self.conn = None
        else:
            conn = [
                conn
                for conn in self.map.connections
                if set(conn.hubs) == set([prev_hub, curr_hub])
            ]
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


class HubSprite(arcade.Sprite):
    """

    A Sprite class to represent hub Hub.

    """

    hub: Hub

    def __init__(self, hub: Hub):
        img_priority = "images/meteor_detailedLarge.png"
        img_blocked = "images/meteor_squareLarge.png"
        img_normal = "images/meteor_large.png"
        img_restricted = "images/meteor_squareDetailedLarge.png"

        if hub.zone == Zone.RESTRICTED:
            img = img_restricted
        elif hub.zone == Zone.BLOCKED:
            img = img_blocked
        elif hub.zone == Zone.PRIORITY:
            img = img_priority
        else:
            img = img_normal

        super().__init__(img, scale=0.5)
        self.hub = hub
        self.center_x = hub.x * 100
        self.center_y = hub.y * 100

        self.label = arcade.Text(
            f"{len(self.hub.drones)}/{self.hub.max_drones}",
            self.center_x,
            self.center_y,
            color=arcade.color.WHITE,
            anchor_x="center",
            anchor_y="center",
            font_size=6,
        )

    def draw_label(self) -> None:
        """

        Draws a line representing a connection between two hubs.

        Returns: None.

        """
        self.label.text = f"{len(self.hub.drones)}/{self.hub.max_drones}"
        self.label.x = self.center_x
        self.label.y = self.center_y + 30
        self.label.draw()


class Visualizer(arcade.Window):
    """
    The Simulation visualizer class.

    """

    map: Map

    scene: Scene
    turn: int
    turn_text: arcade.Text
    turn_max: int
    ui_camera: arcade.Camera2D

    def __init__(self, map: Map):
        super().__init__(1920, 1080, title="Fly-in")
        self.map = map
        self.turn_max = max(len(drone.path) for drone in map.drones) - 1
        self.turn = 0
        self.turn_text = arcade.Text(
            f"turn: {self.turn}/{self.turn_max}", 50, 50, font_size=24
        )
        self.ui_camera = arcade.Camera2D()
        self.camera = arcade.Camera2D()
        self.background_color = arcade.csscolor.BLACK
        self.setup()

    def setup(self) -> None:
        """
        Called on start and resets, used to reset to the start state.
        clears all drones from all connections and hubs, sets the scene and
        zoom the camera to fit it inside.

        """
        self.turn = 0
        self.scene = arcade.Scene()
        self.scene.add_sprite_list("hubs", use_spatial_hash=True)
        self.scene.add_sprite_list("drones")

        for conn in self.map.connections:
            conn.drones.clear()

        for hub in self.map.hubs:
            hub.drones.clear()
            self.scene.add_sprite("hubs", HubSprite(hub))

        for hub_sprite in self.scene["hubs"]:
            hub_sprite.draw_label()

        for drone in self.map.drones:
            self.scene.add_sprite("drones", DroneSprite(drone, self.map))
            drone.path[0].drones.append(drone)

        self.fit_camera()

    def fit_camera(self) -> None:
        """
        Fits the hubs to the camera, so as to contain all of them in the view.
        finds the range of the x and y ratios to the screen and then uses the
        minimum.

        """
        PADDING = 25

        xs = [hub.x * 100 for hub in self.map.hubs]
        ys = [hub.y * 100 for hub in self.map.hubs]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        cx = (min_x + max_x) / 2
        cy = (min_y + max_y) / 2
        self.camera.position = (cx, cy)

        content_w = (max_x - min_x) + PADDING * 2
        content_h = (max_y - min_y) + PADDING * 2

        zoom_x = self.width / content_w
        zoom_y = self.height / content_h

        self.camera.zoom = min(zoom_x, zoom_y)

    def draw_connections(self) -> None:
        """
        Draws all connections with their line and label as the current and max
        capacities.
        """
        for conn in self.map.connections:
            hub1, hub2 = conn.hubs
            if hub2.zone == Zone.PRIORITY:
                color = arcade.color.BLUE
            elif hub2.zone == Zone.RESTRICTED:
                color = arcade.color.YELLOW
            elif hub2.zone == Zone.BLOCKED:
                color = arcade.color.RED
            else:
                color = arcade.color.COOL_GREY

            arcade.draw_line(
                hub1.x * 100,
                hub1.y * 100,
                hub2.x * 100,
                hub2.y * 100,
                color,
                2 * conn.max_link_capacity,
            )
            arcade.Text(
                f"{len(conn.drones)}/{conn.max_link_capacity}",
                (hub1.x + hub2.x) * 100 / 2,
                (hub1.y + hub2.y) * 100 / 2 + 5,
                font_size=6,
            ).draw()

    def next_turn(self, prev: int) -> None:
        """
        Triggers all drone sprites' move_drone to move to the next hub's
        coordinates.

        Args:
          prev: int: the previous turn, used to let the drone know which hub to
            remove itself from.

        Returns: None

        """
        if 0 <= self.turn <= self.turn_max:
            for drone in self.scene["drones"]:
                drone.move_drone(self.turn, prev)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """
        User control function, to reset, quit and progress to the next move.

        Args:
          symbol: int: the key pressed.
          modifiers: int: modifier key, like alt, shift... etc, but not used.

        Returns: None.

        """
        prev: int = self.turn

        if symbol == arcade.key.R:
            self.setup()

        elif symbol == arcade.key.RIGHT:
            if self.turn < self.turn_max:
                self.turn += 1
                self.next_turn(prev)

        elif symbol == arcade.key.LEFT:
            if self.turn > 0:
                self.turn -= 1
                self.next_turn(prev)

        elif symbol == arcade.key.Q:
            exit(0)

    def on_draw(self) -> None:
        """
        Draws everything, called by the framework on every tick.
        Sets the camera, draw connections, scene, and texts.

        """
        self.clear()
        self.camera.use()
        self.draw_connections()
        self.scene.draw()
        for hub_sprite in self.scene["hubs"]:
            hub_sprite.draw_label()
        self.ui_camera.use()
        self.turn_text.text = f"Turn: {self.turn}/{self.turn_max}"
        self.turn_text.draw()

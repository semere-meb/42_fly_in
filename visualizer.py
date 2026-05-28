import arcade
from arcade.scene import Scene

from graph import Graph
from models import Drone, Hub, Map, Zone


class DroneSprite(arcade.Sprite):
    drone: Drone
    label: str
    in_transit: bool

    def __init__(self, drone: Drone):
        self.drone = drone

        super().__init__("images/ship_F.png", scale=0.2, angle=90)

        self.label = str(self.drone.id)
        self.center_x = self.drone.path[0].x * 100
        self.center_y = self.drone.path[0].y * 100
        self.in_transit = False

    def move_drone(self, turn: int) -> None:
        if 0 <= turn < len(self.drone.path):
            if self.drone.path[turn].zone == Zone.RESTRICTED:
                self.in_transit = not self.in_transit

            if self.in_transit:
                self.center_x = (
                    (self.drone.path[turn - 1].x + self.drone.path[turn].x)
                    * 100
                    / 2
                )
                self.center_y = (
                    (self.drone.path[turn - 1].y + self.drone.path[turn].y)
                    * 100
                    / 2
                )
            else:
                self.center_x = self.drone.path[turn].x * 100
                self.center_y = self.drone.path[turn].y * 100

            # if turn == 0:
            #     self.degree = 0
            # else:
            #     dx = self.drone.path[turn].x - self.drone.path[turn - 1].x
            #     dy = self.drone.path[turn].y - self.drone.path[turn - 1].y
            #     self.angle = math.degrees(math.atan2(dy, dx))


class HubSprite(arcade.Sprite):
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
        self.label.x = self.center_x
        self.label.y = self.center_y + 30
        self.label.draw()


class Visualizer(arcade.Window):
    map: Map
    graph: dict[Hub, dict[Hub, float]]
    res: str

    scene: Scene
    turn: int
    turn_txt: arcade.Text
    turn_max: int

    def __init__(self, map: Map, graph: Graph, res: str):
        super().__init__(1920, 1080, title="Fly-in")
        self.map = map
        self.graph = graph.graph_network
        self.res = res
        self.scene = Scene()
        self.setup()
        self.turn = 0
        x, y = self.scene["hubs"].center
        self.turn_text = arcade.Text(f"{self.turn}", x, y)
        self.turn_max = max(len(drone.path) for drone in map.drones) - 1

    def setup(self) -> None:
        self.camera = arcade.Camera2D()
        self.background_color = arcade.csscolor.BLACK
        self.scene = arcade.Scene()
        self.scene.add_sprite_list("hubs", use_spatial_hash=True)
        self.scene.add_sprite_list("drones")

        for hub in self.map.hubs:
            hubsprite = HubSprite(hub)
            self.scene.add_sprite("hubs", hubsprite)

        for drone in self.map.drones:
            self.scene.add_sprite("drones", DroneSprite(drone))

        self.fit_camera()

    def fit_camera(self) -> None:
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

    def next_turn(self) -> None:
        if 0 <= self.turn <= self.turn_max:
            for drone in self.scene["drones"]:
                drone.move_drone(self.turn)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol not in (arcade.key.R, arcade.key.RIGHT):
            return

        if symbol == arcade.key.R:
            self.turn = 0

        elif symbol == arcade.key.RIGHT:
            if self.turn < self.turn_max:
                self.turn += 1

        # elif symbol == arcade.key.LEFT:
        #     if self.turn > 0:
        #         self.turn -= 1

        self.next_turn()

    def on_draw(self) -> None:
        self.clear()
        self.camera.use()
        self.draw_connections()
        self.scene.draw()
        for hub_sprite in self.scene["hubs"]:
            hub_sprite.draw_label()

import arcade

from graph import Graph
from models import Map, Zone


class Visualizer(arcade.Window):
    map: Map
    graph: Graph

    def __init__(self, map: Map, graph: Graph):
        super().__init__(1920, 1080, title="Fly-in")
        self.map = map
        self.graph = graph

        self.scene = None
        self.camera = None
        self.gui_camera = None
        self.tick_counter = 0

        self.hub_sprite = None
        self.drone_texture = (
            ":resources:/images/space_shooter/playerShip3_orange.png"
        )
        self.hub_textures = {
            Zone.PRIORITY: "images/ufoGreen.png",
            Zone.NORMAL: "images/ufoBlue.png",
            Zone.RESTRICTED: "images/ufoYellow.png",
            Zone.BLOCKED: "images/ufoRed.png",
        }

        self.setup()

    def setup(self):
        self.camera = arcade.Camera2D()
        self.background_color = arcade.csscolor.SKY_BLUE
        self.scene = arcade.Scene()
        self.scene.add_sprite_list("hubs", use_spatial_hash=True)
        self.scene.add_sprite_list("drones")

        for hub in self.map.hubs:
            hub_sprite = arcade.Sprite(self.hub_textures[hub.zone], scale=0.5)
            hub_sprite.center_x = hub.x * 100
            hub_sprite.center_y = hub.y * 100
            self.scene.add_sprite("hubs", hub_sprite)

        for _ in range(self.map.nb_drones):
            drone_sprite = arcade.Sprite(self.drone_texture, scale=0.3)
            drone_sprite.center_x = self.map.start.x * 100
            drone_sprite.center_y = self.map.start.y * 100
            drone_sprite.angle = 90
            self.scene.add_sprite("drones", drone_sprite)

        self._fit_camera()

    def _fit_camera(self):
        PADDING = 100

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

    def on_draw(self):
        self.clear()
        self.camera.use()

        for conn in self.map.connections:
            hub1, hub2 = conn.hubs
            arcade.draw_line(
                hub1.x * 100,
                hub1.y * 100,
                hub2.x * 100,
                hub2.y * 100,
                arcade.csscolor.GRAY,
                6,
            )

        self.scene.draw()

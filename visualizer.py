import arcade

from models import Hub, Map


class HubSprite(arcade.Sprite):
    hub: Hub

    def __init__(self, hub: Hub):
        texture = arcade.make_circle_texture(100, hub.color, hub.name)
        super().__init__(texture, scale=0.5)
        self.hub = hub
        self.center_x = hub.x * 100
        self.center_y = hub.y * 100

        self.label = arcade.Text(
            f"{self.hub.name}:{self.hub.max_drones}",
            self.center_x,
            self.center_y,
            color=tuple(255 - r for r in self.hub.color)[:3],
            anchor_x="center",
            anchor_y="center",
            font_size=6,
        )

    def draw_label(self) -> None:
        self.label.x = self.center_x
        self.label.y = self.center_y
        self.label.draw()


class Visualizer(arcade.Window):
    map: Map

    def __init__(self, map: Map):
        super().__init__(1920, 1080, title="Fly-in")
        self.map = map

        self.scene = None
        self.camera = None
        self.gui_camera = None
        self.tick_counter = 0

        self.hub_sprite = None

        self.setup()

    def setup(self):
        self.camera = arcade.Camera2D()
        self.background_color = arcade.csscolor.LIGHT_CORAL
        self.scene = arcade.Scene()
        self.scene.add_sprite_list("hubs", use_spatial_hash=True)
        self.scene.add_sprite_list("drones")

        for hub in self.map.hubs:
            hub_sprite = HubSprite(hub)
            self.scene.add_sprite("hubs", hub_sprite)

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

    def draw_connections(self) -> None:
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
            arcade.Text(
                str(int(self.map.graph[hub1][hub2])),
                (hub1.x + hub2.x) * 100 / 2,
                (hub1.y + hub2.y) * 100 / 2 + 5,
            ).draw()

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.draw_connections()
        self.scene.draw()
        for hub_sprite in self.scene["hubs"]:
            hub_sprite.draw_label()

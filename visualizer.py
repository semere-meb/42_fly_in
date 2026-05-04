import arcade

from graph import Graph
from models import Map


class Visualizer(arcade.Window):
    def __init__(self, map: Map, graph: Graph):
        super().__init__(title="Fly-in")
        self.scene = None
        self.camera = None
        self.gui_camera = None
        self.tick_counter = 0

    def setup(self):
        self.clear()
        self.background_color = arcade.csscolor.SKY_BLUE
        self.scene = arcade.Scene()

    def on_draw(self):
        self.clear()
        self.scene.draw()

    def on_update(self, delta_time):
        pass

    # def on_key_press(self, key, modifiers):
    #     pass

    # def on_key_release(self, key, modifiers):
    #     pass

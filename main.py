import arcade

from graph import Graph
from models import Map
from parser import Parser
from visualizer import Visualizer


def main() -> None:

    parser = Parser()
    parser.parse_args()
    map: Map = parser.parse_map()

    graph = Graph(map)
    # dist = graph.dijkstra(map.start.name)

    vis = Visualizer(map, graph)
    vis.setup()
    arcade.run()


if __name__ == "__main__":
    main()

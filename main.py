from models import Map
from parser import Parser
from pathfinder import Pathfinder
from visualizer import Visualizer


def main() -> None:

    parser = Parser()
    parser.parse_args()
    map: Map = parser.parse_map()

    pathfinder = Pathfinder(map)
    pathfinder.get_all_paths()
    # for path in pathfinder.paths:
    #     for hub in path:
    #         print(hub.name, end=" => ")

    #     print()

    vis = Visualizer(map)
    vis.run()


if __name__ == "__main__":
    main()

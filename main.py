from engine import Engine
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
    pathfinder.cal_path_cost()
    for length, throughput, cost, path in pathfinder.path_rank:
        for hub in path:
            print(hub.name, end=" => ")
        print(f"[L={length},T={throughput},C={cost}]")

    engine = Engine(map, pathfinder)
    engine.run()
    vis = Visualizer(map)
    vis.run()


if __name__ == "__main__":
    main()

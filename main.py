from engine import Engine
from graph import Graph
from parser import Parser
from pathfinder import Pathfinder
from scheduler import Scheduler


def main() -> None:
    parser = Parser()
    parser.parse_args()
    map = parser.parse_map()
    graph = Graph(map)
    pathfinder = Pathfinder(graph)
    _, paths = pathfinder.edmonds_karp(graph.source, graph.sink)

    scheduler = Scheduler(map, paths)
    scheduler.assign_paths()

    engine = Engine(map=map)
    engine.run()

    # exit(len(map.drones[-1].path) - 1)


if __name__ == "__main__":
    main()

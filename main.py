from engine import Engine
from graph import Graph
from parser import Parser
from pathfinder import Pathfinder
from scheduler import Scheduler
from visualizer import Visualizer


def main() -> None:
    parser = Parser()
    parser.parse_args()
    map = parser.parse_map()
    graph = Graph(map)
    pathfinder = Pathfinder(graph)
    paths = pathfinder.get_paths(graph.source, graph.sink)

    scheduler = Scheduler(map, paths)
    scheduler.assign_paths()

    engine = Engine(map)
    engine.run()

    vis = Visualizer(map, graph, engine.res)
    vis.run()


if __name__ == "__main__":
    main()

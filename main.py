from models import Map
from parser import Parser
from pathfinder import Pathfinder


def main() -> None:
    parser = Parser()
    parser.parse_args()
    map: Map = parser.parse_map()
    map.to_graph()

    pathfinder = Pathfinder(map)
    flow, paths = pathfinder.edmonds_karp(
        f"{map.start.name}_out", f"{map.end.name}_in"
    )
    print(f"Number of paths: {len(paths)}, max flow: {flow}")
    for i, (f, p) in enumerate(paths):
        print(f"Path {i + 1}: {[hub for hub in p]} [F={f}, L={len(p) - 1}]")


if __name__ == "__main__":
    main()

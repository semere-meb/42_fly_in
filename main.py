import math

from graph import Graph
from parser import Parser
from pathfinder import Pathfinder


def main() -> None:
    parser = Parser()
    parser.parse_args()
    map = parser.parse_map()
    graph = Graph(map)
    pathfinder = Pathfinder(graph)
    flow, paths = pathfinder.edmonds_karp(graph.source, graph.sink)

    print(f"N: {map.nb_drones}, F: {flow}, P: {len(paths)}")
    clean_paths: list[tuple[float, float, list[str]]] = []
    for f, c, p in paths:
        clean_path = []
        for n in p:
            name = n.name.split("-")[0]
            if name not in clean_path:
                clean_path.append(name)
        clean_paths.append((f, c, clean_path))
        print(f"{clean_path} [f={f}, C={c}, L={len(clean_path) - 1}]")

    clean_paths.sort(key=lambda x: x[2])
    _, cost, __ = paths[-1]
    cost = round(cost)
    print(f"len: {cost}, nb_drones: {map.nb_drones}, flow: {flow}")
    print(f"makespan: {cost + math.ceil(map.nb_drones / flow) - 1}")
    pp: str = clean_paths[0][2][-1]
    print(pp)


if __name__ == "__main__":
    main()

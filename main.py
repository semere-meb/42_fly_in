from graph import Graph
from models import Map
from parser import Parser


def main() -> None:

    parser = Parser()
    parser.parse_args()
    map: Map = parser.parse_map()

    graph = Graph(map)
    dist = graph.dijkstra(map.start.name)
    if dist:
        for key in dist:
            print(key, "=>", graph.dist[key])


if __name__ == "__main__":
    main()

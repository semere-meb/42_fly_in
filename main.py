from models import Map
from parser import Parser


def main() -> None:

    parser = Parser()
    parser.parse_args()
    map: Map = parser.parse_map()

    with open("dump.json", mode="w") as out:
        out.write(map.model_dump_json(indent=4))

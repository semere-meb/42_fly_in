import sys

from src.parser import Parser


def main() -> None:
    parser = Parser()
    map_path = parser.parse_args()

    if not map_path.is_file():
        print("Map file not found.")
        sys.exit(1)

    parser.parse_map(map_path)

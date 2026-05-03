import re
from argparse import ArgumentParser
from pathlib import Path

from pydantic import ValidationError

from errors import ParseError
from models import Connection, Hub, Map, Zone


class Parser:
    map_path: Path

    @staticmethod
    def _separate_line(ln: int, string: str) -> tuple[str, str]:
        match = re.search(r"\[.*\]", string)

        if match:
            if len(string) > match.endpos:
                raise ParseError(
                    f"{ln}, Extraneous syntax at column {match.endpos + 1}"
                )
            return (
                string[: match.start()].strip(),
                string[match.start() :].strip(),
            )
        else:
            return (string.strip(), "")

    @staticmethod
    def _get_hub_by_name(name: str, hubs: list[Hub]) -> Hub | None:
        res_hub = None

        for hub in hubs:
            if hub.name == name:
                res_hub = hub

        return res_hub

    def parse_args(self) -> None:

        map_default: str = "maps/easy/01_linear_path.txt"

        parser = ArgumentParser(
            prog="python -m src",
            description="Efficient drone fleet routing system",
        )

        parser.add_argument(
            "-m",
            "--map",
            default=map_default,
            help=f"Path to the map file. Default: {map_default}",
        )

        self.map_path = Path(parser.parse_args().map)

    def parse_map(self) -> Map:
        hubs: list[Hub] = []
        connections: list[Connection] = []

        if not self.map_path.is_file():
            raise ParseError("Map file not found.")

        try:
            with open(self.map_path) as map_file:
                all_lines = map_file.readlines()
        except IOError as e:
            raise ParseError("Issue openning map file.") from e

        lines: dict[int, str] = {
            (all_lines.index(line) + 1): line
            for line in all_lines
            if not line.startswith("#") and not line.isspace()
        }

        if not lines:
            raise ParseError("Empty map file.")

        try:
            first_ln = min(sorted(lines))
            key, value = lines[first_ln].split(":")
            if key.strip() != "nb_drones":
                raise ParseError(
                    f"{first_ln}, Number of drones not declared in first line"
                )
            nb_drones = int(value)
        except Exception as e:
            raise ParseError(f"{first_ln}, Malformed map file: {e}") from e

        try:
            for ln, line in sorted(lines.items())[1:]:
                key, values = line.strip().split(":")

                key = key.strip()
                if key == "hub":
                    hubs.append(self.parse_hub(ln, values))
                elif key == "start_hub":
                    hub = self.parse_hub(ln, values, is_start=True)
                    hubs.append(hub)
                    start_hub = hub
                elif key == "end_hub":
                    hub = self.parse_hub(ln, values, is_end=True)
                    hubs.append(hub)
                    end_hub = hub
                elif key == "connection":
                    conn = self.parse_conn(ln, values, hubs, connections)
                    connections.append(conn)
                else:
                    raise ParseError(f"{ln}, Invalid key: '{key}'")

        except ValueError as e:
            raise ParseError(f"{ln}, Malformed entry in map file") from e

        if len([hub for hub in hubs if hub.is_start]) != 1:
            raise ParseError("Must have one and only one start hub.")

        if len([hub for hub in hubs if hub.is_end]) != 1:
            raise ParseError("Must have one and only one end hub.")

        return Map(
            nb_drones=nb_drones,
            start=start_hub,
            end=end_hub,
            hubs=hubs,
            connections=connections,
        )

    def parse_hub(
        self,
        ln: int,
        string: str,
        is_start: bool = False,
        is_end: bool = False,
    ) -> Hub:
        zone = Zone.NORMAL
        color = "blue"
        max_drones = 1

        try:
            mandatory, meta_str = Parser._separate_line(ln, string)
            name, x_str, y_str = mandatory.split()
        except ValueError as e:
            raise ParseError(f"{ln} Invalid syntax for a hub: {string}") from e

        if re.search(r"\s|-", name):
            raise ParseError(f"{ln}, Invalid name for a hub '{name:.20}'")

        try:
            x: int = int(x_str)
            y: int = int(y_str)
        except ValueError as e:
            raise ParseError(f"{ln} Expected integer value. {e}") from e

        for option_str in meta_str[1:-1].split():
            key, val = option_str.split("=")

            if key == "zone":
                if val == "normal":
                    zone = Zone.NORMAL
                elif val == "restricted":
                    zone = Zone.RESTRICTED
                elif val == "blocked":
                    zone = Zone.BLOCKED
                elif val == "priority":
                    zone = Zone.PRIORITY
                else:
                    raise ParseError(f"{ln}, Invalid value '{val}' for 'zone'")

            elif key == "color":
                color = val

            elif key == "max_drones":
                try:
                    max_drones = int(val)
                    if max_drones <= 0:
                        raise ParseError(
                            f"{ln}, A hub must allow at least one drone."
                        )
                except ValueError as e:
                    raise ParseError(
                        f"{ln}, Non-integer value '{val}' for '{key}'"
                    ) from e
            else:
                raise ParseError(f"{ln}, Unexpected metadata name '{key}'")
        try:
            hub = Hub(
                name=name,
                x=x,
                y=y,
                is_start=is_start,
                is_end=is_end,
                color=color,
                zone=zone,
                max_drones=max_drones,
            )
        except ValidationError as e:
            raise ParseError(f"{ln}, Validation error: {e}") from e
        return hub

    def parse_conn(
        self,
        ln: int,
        string: str,
        hubs: list[Hub],
        connections: list[Connection],
    ) -> Connection:
        conn_hubs: list[Hub] = []
        capacity: int = 1

        string = string.strip()
        try:
            if len(string.split()) == 1:
                hubs_str = string
                meta_str = "[]"
            elif len(string.split()) == 2:
                hubs_str, meta_str = string.split()
            hub1_name, hub2_name = hubs_str.split("-")
        except ValueError as e:
            raise ParseError(
                f"{ln}, Malformed connection name '{hubs_str}'"
            ) from e

        for hub_name in (hub1_name, hub2_name):
            if hub := Parser._get_hub_by_name(hub_name, hubs):
                conn_hubs.append(hub)
            else:
                raise ParseError(f"{ln}, Hub '{hub_name}' not found.")

        if self._check_duplicate_connection(connections, hub1_name, hub2_name):
            raise ParseError(
                f"{ln}, Duplicate connection definition: '{hubs_str}'"
            )

        if not meta_str.startswith("[") or not meta_str.endswith("]"):
            raise ParseError(
                f"{ln}, Invalid syntax for connection meta: '{meta_str}'"
            )

        meta_str = meta_str[1:-1]

        if meta_str:
            try:
                key, val = meta_str.strip().split("=")
                if key == "max_link_capacity":
                    capacity = int(val)
                else:
                    raise ParseError(f"{ln}, Invalid metadata key '{key}'")

            except ValueError as e:
                raise ParseError(
                    f"{ln}, Malformed Metadata line '{meta_str}'"
                ) from e

        if capacity <= 0:
            raise ParseError(f"{ln}, Negative value not allowed.")

        try:
            return Connection(hubs=conn_hubs, capacity=capacity)
        except ValidationError as e:
            raise ParseError(f"{ln}, Validation error '{e}'") from e

    def _check_duplicate_connection(
        self,
        connections: list[Connection],
        hub1_name: str,
        hub2_name: str,
    ) -> bool:
        return any(
            set([hub1_name, hub2_name]) == set([hub.name for hub in conn.hubs])
            for conn in connections
        )

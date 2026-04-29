import re
from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError

from src.errors import AppError
from src.models import Connection, Hub, Map, Zone


class ParseError(Exception):
    pass


class HubMetadata(BaseModel):
    zone: Zone
    color: str
    max_drones: int


class Parser:
    @staticmethod
    def get_hub_by_name(name: str, hubs: list[Hub]) -> Hub | None:
        res_hub = None

        for hub in hubs:
            if hub.name == name:
                res_hub = hub

        return res_hub

    def parse_args(self) -> Path:
        """ """

        map_default: str = "maps/easy/01_linear_path.txt"

        parser = ArgumentParser(
            prog="python -m src",
            description="Performs constrained decoding from a prompt",
        )

        parser.add_argument(
            "-m",
            "--map",
            default=map_default,
            help=f"Path to the map file.\n\
                Default: {map_default}",
        )
        return Path(parser.parse_args().map)

    def parse_map(self, map_path: Path) -> Map:
        hubs: list[Hub] = []
        connections: list[Connection] = []
        nb_drones: int

        with open(map_path) as map_file:
            all_lines = map_file.readlines()
        lines = [
            line
            for line in all_lines
            if not line.startswith("#") and not line.isspace()
        ]

        try:
            key, value = lines[0].split(":")
            if key.strip() != "nb_drones":
                raise AppError("Number of drones not declared in first line.")
            nb_drones = int(value)
        except ValueError as e:
            raise AppError(f"Malformed map file: {e}") from e

        try:
            for line in lines:
                key, values = line.strip().split(":")

                key = key.strip()
                if key == "hub":
                    hubs.append(self.parse_hub(values))
                elif key == "start_hub":
                    hub = self.parse_hub(values, is_start=True)
                    hubs.append(hub)
                    start_hub = hub
                elif key == "end_hub":
                    hub = self.parse_hub(values, is_end=True)
                    hubs.append(hub)
                    end_hub = hub
                elif key == "connection":
                    conn = self.parse_conn(values, hubs, connections)
                    connections.append(conn)
                else:
                    raise AppError(f"Invalid key: '{key}'")

        except ValueError as e:
            raise AppError("Malformed entry in map file") from e

        if len([hub for hub in hubs if hub.is_start]) != 1:
            raise AppError("Must have one and only one start hub.")

        if len([hub for hub in hubs if hub.is_end]) != 1:
            raise AppError("Must have one and only one end hub.")

        return Map(
            nb_drones=nb_drones,
            start=start_hub,
            end=end_hub,
            hubs=hubs,
            connections=connections,
        )

    def parse_hub(
        self, string: str, is_start: bool = False, is_end: bool = False
    ) -> Hub:
        name: str
        x: int
        y: int
        meta: HubMetadata

        name, x_str, y_str, meta_str = string.split()

        if re.search(r"\s|-", name):
            raise ParseError(f"Invalid name for a hub {name}")

        try:
            x = int(x_str)
            y = int(y_str)
        except ValueError as e:
            raise ParseError("Invalid value when expecting an integer.") from e

        if not meta_str.startswith("[") or not meta_str.endswith("]"):
            raise ParseError(f"Invalid optional metadata syntax: {meta_str}")

        for option_str in meta_str[1:-1].split():
            options: dict[str, Any] = {}

            key, val = option_str.split("=")

            if key in options.keys():
                raise ParseError(f"Duplicate entry {key} for hub {name}")

            if key == "zone":
                if val == "normal":
                    options["zone"] = Zone.NORMAL
                elif val == "restricted":
                    options["zone"] = Zone.RESTRICTED
                elif val == "blocked":
                    options["zone"] = Zone.BLOCKED
                elif val == "priority":
                    options["zone"] = Zone.PRIORITY
                else:
                    raise AppError(f"Invalid value '{val}' for 'zone'")

            if key == "color":
                options["color"] = val

            elif key == "max_drones":
                try:
                    options["max_drones"] = int(val)
                except ValueError as e:
                    raise AppError(
                        f"Non-integer value '{val}' for '{key}'"
                    ) from e
            else:
                raise AppError(f"Unexpected metadata name '{key}'")
            meta = HubMetadata(
                zone=options["zone"],
                color=options["color"],
                max_drones=options["max_drones"],
            )
        try:
            hub = Hub(
                name=name,
                x=x,
                y=y,
                is_start=is_start,
                is_end=is_end,
                color=meta.color,
                zone=meta.zone,
                max_drones=meta.max_drones,
            )
        except ValidationError as e:
            raise AppError(f"Validation error: {e}") from e
        return hub

    def parse_conn(
        self, string: str, hubs: list[Hub], connections: list[Connection]
    ) -> Connection:
        conn_hubs: list[Hub] = []
        max_links: int = 1

        try:
            hubs_str, meta_str = string.split()
            hub1_name, hub2_name = hubs_str.strip().split("-")
        except ValueError as e:
            raise AppError(f"Malformed connection name '{hubs_str}'") from e

        for hub_name in (hub1_name, hub2_name):
            if hub := Parser.get_hub_by_name(hub_name, hubs):
                conn_hubs.append(hub)
            else:
                raise AppError(f"Hub '{hub_name}' not found.")

        if any(set(conn.hubs) == set(conn_hubs) for conn in connections):
            raise AppError(f"Duplicate connection definition: '{hubs_str}'")

        if not meta_str.startswith("[") or meta_str.endswith("]"):
            raise AppError(f"Invalid syntax for connection meta: '{meta_str}'")

        meta_str = meta_str[1:-1]

        if meta_str:
            try:
                key, val = meta_str.strip().split("=")
                if key == "max_links":
                    max_links = int(val)
                else:
                    raise AppError(f"Invalid metadata key '{key}'")
            except ValueError as e:
                raise AppError(f"Malformed Metadata line '{meta_str}'") from e

        try:
            return Connection(hubs=conn_hubs, max_links=max_links)
        except ValidationError as e:
            raise AppError(f"Validation error '{e}'") from e

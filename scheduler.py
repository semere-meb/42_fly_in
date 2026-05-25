from errors import SchedulerError
from models import Drone, Hub, Map
from pathfinder import Path


class Scheduler:
    paths: list[Path] = []
    drones: list[Drone]
    map: Map

    def __init__(
        self,
        map: Map,
        paths: list[Path],
    ):
        self.map = map
        self.drones = map.drones
        for path in paths:
            hubs: list[Hub] = []
            for n in path.hubs:
                name, hub_type = n.name.split("-")
                hub = self.map.get_hub(name)
                if hub not in hubs:
                    hubs.append(hub)
                if hub_type == "mid":
                    hubs.append(hub)

            self.paths.append(Path(path.flow, path.cost, hubs))

    def assign_paths(self) -> None:
        i = 0
        while i < len(self.drones):
            self.paths.sort(key=lambda path: path.cost)
            path = self.paths[0]

            for j in range(path.flow):
                self.drones[i + j].path = path.hubs.copy()
            path.cost += 1
            path.hubs.insert(0, self.map.start)
            i += path.flow

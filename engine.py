from models import Map
from pathfinder import Pathfinder


class Engine:
    map: Map
    pathfinder: Pathfinder

    def __init__(self, map: Map, pathfinder: Pathfinder):
        self.map = map
        self.pathfinder = pathfinder

    def assign_drones(self) -> None:
        drones = self.map.drones
        paths = self.pathfinder.path_rank

        total_T = sum([T for _, T, _, _ in paths])

        index = 0
        for i in range(len(drones)):
            # rem = i%total_T
            # index = rem - sum([T for _, T, _, _ in paths[]])
            # drones[i].path = paths[]
            pass

    def run(self) -> None:
        self.assign_drones()

from models import DroneState, Map, Zone


class Engine:
    """
    Moves the drones through the map.

    """

    map: Map
    res: str

    def __init__(self, map: Map):
        self.map = map
        self.res = ""

    def run(self) -> None:
        """
        Prints the turns as the drones move through the hubs, turn-by-turn.

        """
        drones = self.map.drones
        i = 1
        while any([drone.state != DroneState.DONE for drone in drones]):
            line: str = ""
            for drone in drones:
                if drone.state == DroneState.DONE:
                    continue

                curr = drone.path[i]

                if curr != self.map.start:
                    drone.state = DroneState.EN_ROUTE

                if curr.zone == Zone.RESTRICTED:
                    drone.in_transit = not drone.in_transit

                if drone.state == DroneState.EN_ROUTE and drone.in_transit:
                    prev = drone.path[i - 1]
                    line += f"D{drone.id}-<{prev.name}-{curr.name}> "
                elif drone.state == DroneState.EN_ROUTE:
                    line += f"D{drone.id}-<{curr.name}> "

                if i == len(drone.path) - 1:
                    drone.state = DroneState.DONE

            i += 1
            if line:
                self.res += line + "\n"
        print(self.res.strip())

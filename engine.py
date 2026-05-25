from pydantic import BaseModel

from models import DroneState, Map, Zone


class Engine(BaseModel):
    map: Map

    def run(self) -> None:
        drones = self.map.drones
        i = 1
        while any([drone.state != DroneState.DONE for drone in drones]):
            for drone in drones:
                if drone.state == DroneState.DONE:
                    continue

                prev = drone.path[i - 1]
                curr = drone.path[i]
                if prev == curr:
                    continue

                if i == len(drone.path) - 1:
                    drone.state = DroneState.DONE
                    print(f"D{drone.id}-<{curr.name}>", end=" ")
                elif (
                    curr.zone == Zone.RESTRICTED
                    and drone.state == DroneState.IN_HUB
                ):
                    drone.state = DroneState.IN_TRANSIT
                    prev = drone.path[i - 1]

                    print(f"D{drone.id}-<{prev.name}-{curr.name}>", end=" ")
                else:
                    drone.state = DroneState.IN_TRANSIT
                    print(f"D{drone.id}-<{curr.name}>", end=" ")
            i += 1
            print()

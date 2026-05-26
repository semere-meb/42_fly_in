from pydantic import BaseModel

from models import DroneState, Map, Zone


class Engine(BaseModel):
    map: Map

    def run(self) -> None:
        drones = self.map.drones
        i = 1
        while any([drone.state != DroneState.DONE for drone in drones]):
            for drone in drones:
                # skip if done
                if drone.state == DroneState.DONE:
                    continue

                curr = drone.path[i]

                # update if started
                if curr != self.map.start:
                    drone.state = DroneState.EN_ROUTE

                # check if in_transit
                if curr.zone == Zone.RESTRICTED:
                    drone.in_transit = not drone.in_transit

                if drone.state == DroneState.EN_ROUTE and drone.in_transit:
                    prev = drone.path[i - 1]
                    print(f"D{drone.id}-<{prev.name}-{curr.name}>", end=" ")
                elif drone.state == DroneState.EN_ROUTE:
                    print(f"D{drone.id}-<{curr.name}>", end=" ")

                # check if done
                if i == len(drone.path) - 1:
                    drone.state = DroneState.DONE

            i += 1
            print()

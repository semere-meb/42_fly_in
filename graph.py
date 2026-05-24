from models import Hub, Map, Zone


class Graph:
    # {hub: {hub, [capacity, cost]}}
    source: Hub
    sink: Hub
    graph: dict[Hub, dict[Hub, list[float]]]

    def __init__(self, map: Map) -> None:
        graph: dict[Hub, dict[Hub, list[float]]] = {}

        for hub in map.hubs:
            if hub.zone == Zone.BLOCKED:
                continue
            in_node = hub.model_copy(update={"name": f"{hub.name}-in"})
            out_node = hub.model_copy(update={"name": f"{hub.name}-out"})
            graph[in_node] = {}
            graph[out_node] = {}

            if hub.zone == Zone.RESTRICTED:
                mid_node = hub.model_copy(update={"name": f"{hub.name}-mid"})
                graph[mid_node] = {}
                graph[in_node][mid_node] = [hub.max_drones, 0]
                graph[mid_node][in_node] = [0, 0]
                graph[mid_node][out_node] = [hub.max_drones, 0]
                graph[out_node][mid_node] = [0, 0]
            else:
                graph[in_node][out_node] = [hub.max_drones, 0]
                graph[out_node][in_node] = [0, 0]

            if hub.is_start:
                self.source = out_node
            if hub.is_end:
                self.sink = in_node

        for conn in map.connections:
            if any([hub.zone == Zone.BLOCKED for hub in conn.hubs]):
                continue
            for src, dst in conn.hubs, reversed(conn.hubs):
                cost = 1.0
                if dst.zone == Zone.RESTRICTED:
                    cost = 2.0
                elif dst.zone == Zone.PRIORITY:
                    cost = 0.99

                src_out: Hub = [
                    hub for hub in graph if hub.name == f"{src.name}-out"
                ][0]
                dst_in: Hub = [
                    hub for hub in graph if hub.name == f"{dst.name}-in"
                ][0]
                graph[src_out][dst_in] = [conn.max_link_capacity, cost]
                graph[dst_in][src_out] = [0, 1]

        self.graph = graph

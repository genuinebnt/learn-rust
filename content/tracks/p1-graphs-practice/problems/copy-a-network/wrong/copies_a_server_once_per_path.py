class Server:
    def __init__(self, name: str, links: "list[Server] | None" = None):
        self.name = name
        self.links = links if links is not None else []


def copy_network(start: "Server | None") -> "Server | None":
    if start is None:
        return None
    seen = set()

    def clone(server):
        copy = Server(server.name)
        seen.add(id(server))
        for other in server.links:
            copy.links.append(clone(other) if id(other) not in seen else Server(other.name))
        return copy

    return clone(start)

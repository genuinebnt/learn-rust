class Server:
    def __init__(self, name: str, links: "list[Server] | None" = None):
        self.name = name
        self.links = links if links is not None else []


def copy_network(start: "Server | None") -> "Server | None":
    if start is None:
        return None
    return Server(start.name, start.links)

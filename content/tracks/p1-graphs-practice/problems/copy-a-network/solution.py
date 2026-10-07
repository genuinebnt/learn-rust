class Server:
    def __init__(self, name: str, links: "list[Server] | None" = None):
        self.name = name
        self.links = links if links is not None else []


def copy_network(start: "Server | None") -> "Server | None":
    if start is None:
        return None
    copies = {start: Server(start.name)}
    stack = [start]
    while stack:
        server = stack.pop()
        for other in server.links:
            if other not in copies:
                copies[other] = Server(other.name)
                stack.append(other)
            copies[server].links.append(copies[other])
    return copies[start]

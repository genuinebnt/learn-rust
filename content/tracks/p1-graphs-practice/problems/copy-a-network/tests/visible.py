from anneal_prelude import check, ensure
from solution import copy_network, Server

from solution import Server


def build(names, edges):
    """Servers by name, with directed links (a, b) in order."""
    servers = {n: Server(n) for n in names}
    for a, b in edges:
        servers[a].links.append(servers[b])
    return servers


def reachable(start):
    seen, order, stack = {id(start)}, [start], [start]
    while stack:
        s = stack.pop()
        for o in s.links:
            if id(o) not in seen:
                seen.add(id(o))
                order.append(o)
                stack.append(o)
    return order


def shape(start):
    """Names and links of everything reachable, by name, so two networks can be compared."""
    return sorted((s.name, [o.name for o in s.links]) for s in reachable(start))


def test_none():
    check("copy_network(None)", copy_network(None), None)


def test_single_server():
    a = build("a", [])["a"]
    copy = copy_network(a)
    ensure(copy is not a, "the copy must be a new Server")
    check("copy_network(a).name", copy.name, "a")


def test_a_chain_is_copied_with_new_objects():
    s = build("abc", [("a", "b"), ("b", "c")])
    copy = copy_network(s["a"])
    check("shape of the copy", shape(copy), shape(s["a"]))
    ensure(not ({id(x) for x in reachable(copy)} & {id(x) for x in reachable(s["a"])}), "no Server may be shared with the original")


def test_a_loop_stays_a_loop():
    s = build("ab", [("a", "b"), ("b", "a")])
    copy = copy_network(s["a"])
    ensure(copy.links[0].links[0] is copy, "following the loop must come back to the copy of a")


def test_a_server_linking_to_itself():
    s = build("a", [("a", "a")])
    copy = copy_network(s["a"])
    ensure(copy.links == [copy], "a must link to its own copy")

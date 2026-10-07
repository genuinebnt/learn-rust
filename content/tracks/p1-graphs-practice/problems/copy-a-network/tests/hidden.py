import random

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


def test_a_diamond_is_copied_once():
    s = build("abcd", [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")])
    copy = copy_network(s["a"])
    ensure(copy.links[0].links[0] is copy.links[1].links[0], "d must be copied once, not once per path")
    check("number of servers in the copy", len(reachable(copy)), 4)


def test_link_order_is_kept():
    s = build("abc", [("a", "c"), ("a", "b")])
    copy = copy_network(s["a"])
    check("names of the links of a, in order", [x.name for x in copy.links], ["c", "b"])


def test_the_original_is_not_changed():
    s = build("abc", [("a", "b"), ("b", "c"), ("c", "a")])
    before = shape(s["a"])
    copy_network(s["a"])
    check("shape of the original", shape(s["a"]), before)


def test_a_start_in_the_middle_of_a_cycle():
    s = build("abc", [("a", "b"), ("b", "c"), ("c", "a")])
    copy = copy_network(s["b"])
    check("names around the copied cycle", [copy.name, copy.links[0].name, copy.links[0].links[0].name], ["b", "c", "a"])
    ensure(copy.links[0].links[0].links[0] is copy, "the cycle must close on the copy of b")


def test_a_long_chain_does_not_overflow_the_stack():
    names = [str(i) for i in range(5000)]
    s = build(names, [(names[i], names[i + 1]) for i in range(4999)])
    check("servers in a copied chain of 5000", len(reachable(copy_network(s["0"]))), 5000)


def test_two_links_to_the_same_server():
    s = build("ab", [("a", "b"), ("a", "b")])
    copy = copy_network(s["a"])
    ensure(len(copy.links) == 2 and copy.links[0] is copy.links[1], "both links must lead to the same copied b")


def test_names_are_copied():
    s = build("xyz", [("x", "y"), ("y", "z")])
    copy = copy_network(s["x"])
    check("names along the copied chain", [copy.name, copy.links[0].name, copy.links[0].links[0].name], ["x", "y", "z"])


def test_random_networks_keep_their_shape():
    rng = random.Random(11)
    for _ in range(100):
        names = [chr(97 + i) for i in range(rng.randint(1, 7))]
        edges = [(rng.choice(names), rng.choice(names)) for _ in range(rng.randint(0, 12))]
        s = build(names, edges)
        copy = copy_network(s["a"])
        check(f"shape of the copy for edges {edges}", shape(copy), shape(s["a"]))
        ensure(not ({id(x) for x in reachable(copy)} & {id(x) for x in reachable(s["a"])}), "no Server may be shared")

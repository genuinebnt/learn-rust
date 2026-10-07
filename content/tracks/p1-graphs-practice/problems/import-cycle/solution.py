def find_import_cycle(imports: dict[str, list[str]]) -> list[str] | None:
    on_path = set()
    done = set()

    for root in list(imports):
        if root in done:
            continue
        path = [root]
        on_path.add(root)
        iterators = [iter(imports.get(root, []))]
        while path:
            nxt = next(iterators[-1], None)
            if nxt is None:
                done.add(path[-1])
                on_path.discard(path[-1])
                path.pop()
                iterators.pop()
            elif nxt in on_path:
                return path[path.index(nxt):]
            elif nxt not in done:
                path.append(nxt)
                on_path.add(nxt)
                iterators.append(iter(imports.get(nxt, [])))
    return None

def find_import_cycle(imports: dict[str, list[str]]) -> list[str] | None:
    if not imports:
        return None
    root = next(iter(imports))
    path, on_path = [root], {root}
    iterators = [iter(imports.get(root, []))]
    while path:
        nxt = next(iterators[-1], None)
        if nxt is None:
            on_path.discard(path.pop())
            iterators.pop()
        elif nxt in on_path:
            return path[path.index(nxt):]
        elif nxt not in path:
            path.append(nxt)
            on_path.add(nxt)
            iterators.append(iter(imports.get(nxt, [])))
    return None

def find_import_cycle(imports: dict[str, list[str]]) -> list[str] | None:
    seen = set()
    for root in imports:
        stack = [root]
        while stack:
            m = stack.pop()
            if m in seen:
                return [m]
            seen.add(m)
            stack.extend(imports.get(m, []))
    return None

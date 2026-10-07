def count_rooms(plan: list[str]) -> int:
    return sum(row.count(".") for row in plan)

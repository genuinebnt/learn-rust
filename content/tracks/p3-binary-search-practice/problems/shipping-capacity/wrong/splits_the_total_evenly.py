def min_capacity(weights: list[int], days: int) -> int:
    return max(max(weights), -(-sum(weights) // days))

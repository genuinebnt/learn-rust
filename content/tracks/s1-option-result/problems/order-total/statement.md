Each line is `(price_cents, qty)` as text. Return the sum of `price * qty` over all lines, or `None` if
any field isn't a `u64` or any product or the running total doesn't fit in a `u64`.

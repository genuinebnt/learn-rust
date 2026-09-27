`set(key, value, t)` stores `value` for `key` at time `t`. `get(key, t)` returns the value set at the latest
time `≤ t`, or `None`. Times can arrive in any order.

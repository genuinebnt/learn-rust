A network has `n` nodes labelled 1 to n and a list of directed, weighted edges
`times[i] = (u, v, w)`: a signal takes `w` ms to travel from u to v.

A signal is sent from node `k`. Return how long it takes every node to receive it,
or `None` if some node can't be reached.

```rust
pub fn network_delay(
    times: &[(usize, usize, u32)],
    n: usize,
    k: usize,
) -> Option<u32>
```

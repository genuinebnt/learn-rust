Row 1 is `0`. Each next row replaces every `0` in the previous row with `01` and every `1` with `10`, so the
rows start `0`, `01`, `0110`, `01101001`. Row `n` has `2^(n-1)` symbols.

Return the `k`-th symbol of row `n`, counting from **1**.

`equations[i] = (a, b)` with `values[i]` means `a / b = values[i]`. For each query `(c, d)` return
`Some(c / d)` if the equations determine it, or `None` if they don't (including when `c` or `d` never
appears in an equation).

You have to multiply a chain of matrices. `dims` lists the sizes: matrix `i` has `dims[i]` rows and `dims[i + 1]` columns (so `len(dims) - 1` matrices). Multiplying an `a × b` matrix by a `b × c` matrix costs `a * b * c` scalar multiplications and gives an `a × c` matrix. Matrix multiplication is **associative**, so you may choose the bracketing, but not reorder the matrices.

Return the fewest scalar multiplications needed for the whole chain. With fewer than two matrices the answer is `0`.

```python
cheapest_multiplication([10, 30, 5, 60])      # 4500: (A B) C = 1500 + 3000
cheapest_multiplication([40, 20, 30, 10, 30]) # 26000
```

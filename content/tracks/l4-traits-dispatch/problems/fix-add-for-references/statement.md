`sum_all` doesn't compile: `Poly` only adds by value, and `p` is a `&Poly`. Make these work without cloning
a polynomial:

- `poly + &other`, reusing `poly`'s buffer;
- `&a + &b`, leaving both usable;
- `poly += &other`.

Results never end in zeros.

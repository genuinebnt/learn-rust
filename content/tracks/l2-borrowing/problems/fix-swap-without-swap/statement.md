None of these compiles: each holds two borrows into `v` at once. Fix them without `swap`, `rotate_*`,
or copying any string you don't have to. Two of them never need two live borrows at all. The third
does, except in one case.

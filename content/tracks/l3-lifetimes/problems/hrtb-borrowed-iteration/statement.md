`Stats<C>` owns any collection of `u32` that can be iterated by reference: `Vec`, arrays,
`VecDeque`, `BTreeSet`… Add the bound that makes this work, then implement the methods. None of
them may consume or copy the collection.

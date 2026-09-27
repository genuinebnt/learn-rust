Write four methods of a singly linked list, each by walking a `&mut` cursor down the list: `push_back`,
`insert_sorted`, `remove_if` and `last_mut`. Lists in the tests are long, so no recursion (that's also
why `Drop` is written out).

The shortest cursor loops for two of these are rejected by today's borrow checker even though they're
sound. When that happens, rearrange the loop rather than reaching for `unsafe` or a second pass.

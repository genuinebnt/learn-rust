`add_path_sums` should replace every value with the sum of the values on the path from the root down to that
node. It panics with `already borrowed: BorrowMutError` instead. Make it work by changing how the node is
borrowed (at most 3 changed lines).

`Cart` uses a `RefCell` to get around a borrow error that a split borrow solves. Remove the `RefCell`. Keep the same public methods.

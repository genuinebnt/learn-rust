`Cart` wraps every field in a `RefCell` to get around borrow errors, and still panics at run time in
two of its methods. Remove every `RefCell` (and `Cell`): take `&mut self` where a method changes the
cart, and let the compiler's split borrows do the work. The public methods keep their names, arguments
and results.

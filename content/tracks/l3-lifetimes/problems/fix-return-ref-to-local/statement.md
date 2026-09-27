None of these compiles: each returns a reference to something the function itself owns, which dies at
the end of the call. Change the return types (and for `longest_file_name`, the parameter) so that
each result owns what it must and borrows what it can. `longest_file_name` also has a bug the compiler
can't see; the doc comment is the spec.

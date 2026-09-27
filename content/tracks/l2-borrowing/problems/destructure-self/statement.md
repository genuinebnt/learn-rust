Write the transitions of a small worker state machine. The job name moves from state to state as the
same `String`: no copies (a test compares pointers). Each method updates the state and the log in the
same call, so you'll need borrows of both at once, and to move a field out of a `&mut self`.

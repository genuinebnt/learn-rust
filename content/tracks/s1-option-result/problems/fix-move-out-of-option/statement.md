`start` begins a task and returns the one it interrupted, `finish` moves the current task to `done`, and
`current_mut` lets the caller edit the current task in place. None of them compile:
*cannot move out of `self.current`* (E0507). Fix them without cloning.

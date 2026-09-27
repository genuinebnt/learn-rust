This doesn't compile. Two functions try to write through a reference that only grants reading, even
though a `&mut` appears in their types. Fix the signatures and their callers. `keep_richest` and
`richest_id` are correct: leave them alone.

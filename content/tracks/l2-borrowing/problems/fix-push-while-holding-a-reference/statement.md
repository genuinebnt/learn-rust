`Series::record` doesn't compile. It reads the current record before pushing the new point, and answers
with a reference to the record holder's label. Fix it without copying any label: the `&str` it returns
must be the `String` stored in `labels`.

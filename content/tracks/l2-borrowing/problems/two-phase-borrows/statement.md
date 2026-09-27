`script` doesn't compile, but not every suspicious-looking line is at fault: `v.push(v.len() as i32)`
compiles, and so do several others that read `v` inside a call that mutates it. Fix only the lines the
compiler rejects, keeping each step's meaning.

use std::fmt::Write;

fn put<W: Write>(mut w: W, s: &str) {
    w.write_str(s).expect("writing to a String can't fail");
}

/// Writes `s` into `out`, twice.
pub fn write_twice(out: &mut String, s: &str) {
    put(out, s);
    put(out, s);
}

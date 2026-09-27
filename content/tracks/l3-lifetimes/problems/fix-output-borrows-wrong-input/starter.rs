/// The part of `line` after `prefix`, if `line` starts with it.
pub fn after<'a>(line: &'a str, prefix: &'a str) -> Option<&'a str> {
    line.strip_prefix(prefix)
}

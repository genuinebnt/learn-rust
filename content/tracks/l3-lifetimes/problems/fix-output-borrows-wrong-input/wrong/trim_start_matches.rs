/// The part of `line` after `prefix`, if `line` starts with it.
pub fn after<'a>(line: &'a str, prefix: &str) -> Option<&'a str> {
    Some(line.trim_start_matches(prefix))
}

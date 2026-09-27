/// Each call returns the next number after `start`.
pub fn counter(start: u32) -> impl FnMut() -> u32 {
    let mut n = start;
    move || {
        n += 1;
        n
    }
}

/// A formatter that puts `prefix` before each number: prefix "id-" turns 7 into "id-7".
/// The formatter may outlive the string `prefix` was borrowed from.
pub fn labeler(prefix: &str) -> impl Fn(u32) -> String {
    let prefix = prefix.to_string();
    move |n| format!("{prefix} {n}")
}

/// One check per limit: `checks[i](x)` says whether `x` is above `limits[i]`.
pub fn above_checks(limits: &[u32]) -> Vec<Box<dyn Fn(u32) -> bool>> {
    let mut checks: Vec<Box<dyn Fn(u32) -> bool>> = Vec::new();
    for &limit in limits {
        checks.push(Box::new(move |x| x > limit));
    }
    checks
}

/// One greeting job per name, run later. Each job returns "hello, <name>".
pub fn greeters(names: Vec<String>) -> Vec<Box<dyn FnOnce() -> String>> {
    let mut jobs: Vec<Box<dyn FnOnce() -> String>> = Vec::new();
    for name in names {
        jobs.push(Box::new(move || format!("hello, {name}")));
    }
    jobs
}

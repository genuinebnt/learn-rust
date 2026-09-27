/// Each call returns the next number after `start`.
pub fn counter(start: u32) -> impl FnMut() -> u32 {
    let mut n = start;
    move || {
        n += 1;
        n
    }
}

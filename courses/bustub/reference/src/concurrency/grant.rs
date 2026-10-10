//! Which waiting lock requests may be granted now.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Mode {
    S,
    X,
}

fn compatible(a: Mode, b: Mode) -> bool {
    a == Mode::S && b == Mode::S
}

pub fn grantable(holders: &[Mode], waiting: &[Mode]) -> Vec<usize> {
    let mut granted: Vec<usize> = Vec::new();
    for (i, &m) in waiting.iter().enumerate() {
        let ok = holders.iter().all(|&h| compatible(h, m)) && granted.iter().all(|&g| compatible(waiting[g], m));
        if ok {
            granted.push(i);
        } else {
            // @begin 4d-c4
            break;
            //~ continue;
            // @end
        }
    }
    granted
}

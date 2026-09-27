#[derive(Debug, Clone, Copy)]
pub enum Op {
    Push(i32),
    Pop,
    Insert(usize, i32),
    Remove(usize),
}

pub fn apply(ops: &[Op]) -> Vec<i32> {
    let mut v = Vec::new();
    for &op in ops {
        match op {
            Op::Push(x) => v.push(x),
            Op::Pop => {
                if !v.is_empty() {
                    v.remove(0);
                }
            }
            Op::Insert(i, x) if i <= v.len() => v.insert(i, x),
            Op::Remove(i) if i < v.len() => {
                v.remove(i);
            }
            Op::Insert(..) | Op::Remove(_) => {}
        }
    }
    v
}

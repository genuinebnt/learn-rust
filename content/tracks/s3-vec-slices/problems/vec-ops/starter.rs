#[derive(Debug, Clone, Copy)]
pub enum Op {
    Push(i32),
    Pop,
    Insert(usize, i32),
    Remove(usize),
}

pub fn apply(ops: &[Op]) -> Vec<i32> {
    todo!()
}

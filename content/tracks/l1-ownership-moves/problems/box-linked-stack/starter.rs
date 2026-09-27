/// A stack as a singly linked list of boxed nodes.
pub struct Stack<T> {
    head: Option<Box<Node<T>>>,
    len: usize,
}

struct Node<T> {
    value: T,
    next: Option<Box<Node<T>>>,
}

impl<T> Stack<T> {
    pub fn new() -> Self {
        todo!()
    }

    pub fn len(&self) -> usize {
        todo!()
    }

    pub fn push(&mut self, value: T) {
        todo!()
    }

    pub fn pop(&mut self) -> Option<T> {
        todo!()
    }

    pub fn peek(&self) -> Option<&T> {
        todo!()
    }

    /// Reverses the stack in place, reusing every node.
    pub fn reverse(&mut self) {
        todo!()
    }

    /// Moves the top node, box and all, onto `other`. Returns false when `self` is empty.
    pub fn move_top_to(&mut self, other: &mut Stack<T>) -> bool {
        todo!()
    }

    /// The values, top first.
    pub fn into_vec(self) -> Vec<T> {
        todo!()
    }
}

impl<T> Drop for Stack<T> {
    fn drop(&mut self) {
        // TODO (left empty rather than todo!(): a panic in drop aborts the test binary)
    }
}

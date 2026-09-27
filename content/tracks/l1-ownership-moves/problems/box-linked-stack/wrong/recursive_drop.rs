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
        Stack { head: None, len: 0 }
    }

    pub fn len(&self) -> usize {
        self.len
    }

    pub fn push(&mut self, value: T) {
        let next = self.head.take();
        self.head = Some(Box::new(Node { value, next }));
        self.len += 1;
    }

    pub fn pop(&mut self) -> Option<T> {
        let node = self.head.take()?;
        // Moving out of a Box with `*` is allowed: the Box is consumed and its allocation freed.
        let Node { value, next } = *node;
        self.head = next;
        self.len -= 1;
        Some(value)
    }

    pub fn peek(&self) -> Option<&T> {
        self.head.as_deref().map(|node| &node.value)
    }

    /// Reverses the stack in place, reusing every node.
    pub fn reverse(&mut self) {
        let mut rest = self.head.take();
        while let Some(mut node) = rest {
            rest = node.next.take();
            node.next = self.head.take();
            self.head = Some(node);
        }
    }

    /// Moves the top node, box and all, onto `other`. Returns false when `self` is empty.
    pub fn move_top_to(&mut self, other: &mut Stack<T>) -> bool {
        match self.head.take() {
            Some(mut node) => {
                self.head = node.next.take();
                node.next = other.head.take();
                other.head = Some(node);
                self.len -= 1;
                other.len += 1;
                true
            }
            None => false,
        }
    }

    /// The values, top first.
    pub fn into_vec(mut self) -> Vec<T> {
        let mut out = Vec::with_capacity(self.len);
        while let Some(value) = self.pop() {
            out.push(value);
        }
        out
    }
}

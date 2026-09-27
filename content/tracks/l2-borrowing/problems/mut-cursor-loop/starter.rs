pub struct Node {
    pub val: i32,
    pub next: Option<Box<Node>>,
}

/// A singly linked list. Lists can be long, so nothing here may recurse.
pub struct List {
    head: Option<Box<Node>>,
}

impl List {
    pub fn from_slice(xs: &[i32]) -> Self {
        let mut head = None;
        for &val in xs.iter().rev() {
            head = Some(Box::new(Node { val, next: head }));
        }
        List { head }
    }

    pub fn to_vec(&self) -> Vec<i32> {
        let mut out = Vec::new();
        let mut cur = self.head.as_deref();
        while let Some(node) = cur {
            out.push(node.val);
            cur = node.next.as_deref();
        }
        out
    }

    /// Appends `val` at the end.
    pub fn push_back(&mut self, val: i32) {
        todo!()
    }

    /// Inserts `val` just before the first element greater than `val` (at the end if there's none), so a
    /// sorted list stays sorted and `val` goes after any equal elements.
    pub fn insert_sorted(&mut self, val: i32) {
        todo!()
    }

    /// Removes every element `pred` accepts and returns how many it removed. `pred` sees each element once,
    /// in order.
    pub fn remove_if(&mut self, pred: impl FnMut(i32) -> bool) -> usize {
        todo!()
    }

    /// The last element, for editing.
    pub fn last_mut(&mut self) -> Option<&mut i32> {
        todo!()
    }
}

impl Drop for List {
    fn drop(&mut self) {
        let mut cur = self.head.take();
        while let Some(mut node) = cur {
            cur = node.next.take();
        }
    }
}

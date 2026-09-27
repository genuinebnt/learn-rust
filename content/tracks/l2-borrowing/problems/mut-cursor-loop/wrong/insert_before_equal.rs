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
        let mut cur = &mut self.head;
        while let Some(node) = cur {
            cur = &mut node.next;
        }
        *cur = Some(Box::new(Node { val, next: None }));
    }

    /// Inserts `val` just before the first element greater than `val` (at the end if there's none), so a
    /// sorted list stays sorted and `val` goes after any equal elements.
    pub fn insert_sorted(&mut self, val: i32) {
        let mut cur = &mut self.head;
        while cur.as_ref().is_some_and(|node| node.val < val) {
            cur = &mut cur.as_mut().unwrap().next;
        }
        let rest = cur.take();
        *cur = Some(Box::new(Node { val, next: rest }));
    }

    /// Removes every element `pred` accepts and returns how many it removed. `pred` sees each element once,
    /// in order.
    pub fn remove_if(&mut self, mut pred: impl FnMut(i32) -> bool) -> usize {
        let mut removed = 0;
        let mut cur = &mut self.head;
        loop {
            match cur {
                None => break,
                Some(node) if pred(node.val) => {
                    *cur = node.next.take();
                    removed += 1;
                }
                Some(node) => cur = &mut node.next,
            }
        }
        removed
    }

    /// The last element, for editing.
    pub fn last_mut(&mut self) -> Option<&mut i32> {
        let mut cur = self.head.as_deref_mut()?;
        while let Some(next) = cur.next.as_deref_mut() {
            cur = next;
        }
        Some(&mut cur.val)
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

#[derive(PartialEq, Eq, Clone, Debug)]
pub struct ListNode {
    pub val: i32,
    pub next: Option<Box<ListNode>>,
}

/// Builds a list from values, front to back.
pub fn list(values: &[i32]) -> Option<Box<ListNode>> {
    values.iter().rev().fold(None, |next, &val| Some(Box::new(ListNode { val, next })))
}

/// The list's values, front to back.
pub fn values(mut node: &Option<Box<ListNode>>) -> Vec<i32> {
    let mut out = Vec::new();
    while let Some(n) = node {
        out.push(n.val);
        node = &n.next;
    }
    out
}

pub fn merge(mut a: Option<Box<ListNode>>, mut b: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    // Insert every node of b into a, searching from the head each time.
    while let Some(mut node) = b {
        b = node.next.take();
        let mut slot = &mut a;
        while slot.as_ref().is_some_and(|n| n.val <= node.val) {
            slot = &mut slot.as_mut().expect("checked").next;
        }
        node.next = slot.take();
        *slot = Some(node);
    }
    a
}

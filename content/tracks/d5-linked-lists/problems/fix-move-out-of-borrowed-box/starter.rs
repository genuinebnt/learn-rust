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

/// Removes the first node and returns its value.
pub fn pop_front(head: &mut Option<Box<ListNode>>) -> Option<i32> {
    match head {
        Some(node) => {
            *head = node.next;
            Some(node.val)
        }
        None => None,
    }
}

pub fn push_front(head: &mut Option<Box<ListNode>>, val: i32) {
    let next = head.take();
    *head = Some(Box::new(ListNode { val, next }));
}

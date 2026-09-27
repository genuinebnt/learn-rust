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

pub fn dedup_sorted(head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    // Works for unsorted input too: keep a node only if its value hasn't been kept yet.
    let mut seen: Vec<i32> = Vec::new();
    let mut out = None;
    let mut tail = &mut out;
    let mut cur = head;
    while let Some(mut node) = cur {
        cur = node.next.take();
        if !seen.contains(&node.val) {
            seen.push(node.val);
            tail = &mut tail.insert(node).next;
        }
    }
    out
}

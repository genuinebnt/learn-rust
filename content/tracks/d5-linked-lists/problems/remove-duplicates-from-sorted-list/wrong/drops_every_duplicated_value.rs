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
    let mut out = None;
    let mut tail = &mut out;
    let mut cur = head;
    while let Some(mut node) = cur {
        cur = node.next.take();
        let mut repeated = false;
        while cur.as_ref().is_some_and(|n| n.val == node.val) {
            cur = cur.and_then(|n| n.next);
            repeated = true;
        }
        if !repeated {
            tail = &mut tail.insert(node).next;
        }
    }
    out
}

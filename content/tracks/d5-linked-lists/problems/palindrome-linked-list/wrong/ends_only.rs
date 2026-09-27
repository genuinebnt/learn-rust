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

pub fn is_palindrome(head: Option<Box<ListNode>>) -> bool {
    let first = head.as_ref().map(|n| n.val);
    let mut last = first;
    let mut cur = head.as_deref();
    while let Some(n) = cur {
        last = Some(n.val);
        cur = n.next.as_deref();
    }
    first == last
}

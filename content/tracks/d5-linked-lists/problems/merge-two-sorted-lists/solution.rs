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
    let mut head = None;
    // Where the next node goes: always the `next` of the last node placed.
    let mut tail = &mut head;
    while let (Some(x), Some(y)) = (&a, &b) {
        let src = if x.val <= y.val { &mut a } else { &mut b };
        let mut node = src.take().expect("checked by the loop condition");
        *src = node.next.take();
        tail = &mut tail.insert(node).next;
    }
    *tail = a.or(b);
    head
}

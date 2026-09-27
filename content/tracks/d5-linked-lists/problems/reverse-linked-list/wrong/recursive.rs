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

pub fn reverse(head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    fn go(node: Option<Box<ListNode>>, acc: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
        match node {
            None => acc,
            Some(mut n) => {
                let rest = n.next.take();
                n.next = acc;
                go(rest, Some(n))
            }
        }
    }
    go(head, None)
}

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

pub fn reverse_k_group(head: Option<Box<ListNode>>, k: usize) -> Option<Box<ListNode>> {
    if k < 2 {
        return head;
    }
    let mut probe = head.as_deref();
    for _ in 0..k {
        match probe {
            Some(n) => probe = n.next.as_deref(),
            None => return head,
        }
    }
    let mut rest = head;
    let mut group = None;
    for _ in 0..k {
        let mut node = rest.expect("counted k nodes");
        rest = node.next.take();
        node.next = group;
        group = Some(node);
    }
    // The old first node is now the group's last: attach the rest, reversed the same way.
    let mut last = &mut group;
    while last.as_ref().is_some_and(|n| n.next.is_some()) {
        last = &mut last.as_mut().expect("checked").next;
    }
    last.as_mut().expect("k nodes").next = reverse_k_group(rest, k);
    group
}

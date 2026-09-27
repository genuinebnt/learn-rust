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

pub fn reverse_k_group(mut head: Option<Box<ListNode>>, k: usize) -> Option<Box<ListNode>> {
    if k < 2 {
        return head;
    }
    let mut slot = &mut head;
    while slot.is_some() {
        let mut rest = slot.take();
        let mut group = None;
        let mut taken = 0;
        while taken < k {
            let Some(mut node) = rest else { break };
            rest = node.next.take();
            node.next = group;
            group = Some(node);
            taken += 1;
        }
        *slot = group;
        for _ in 0..taken {
            slot = &mut slot.as_mut().expect("in the group").next;
        }
        *slot = rest;
    }
    head
}

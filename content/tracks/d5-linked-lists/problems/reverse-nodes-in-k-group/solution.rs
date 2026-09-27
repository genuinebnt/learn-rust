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
    // `slot` is where the next group starts: `head`, then the `next` of each reversed group's last node.
    let mut slot = &mut head;
    loop {
        let mut probe = slot.as_deref();
        let mut have = 0;
        while have < k {
            let Some(node) = probe else { break };
            probe = node.next.as_deref();
            have += 1;
        }
        if have < k {
            break;
        }
        // Detach k nodes, reversing them as they come off.
        let mut rest = slot.take();
        let mut group = None;
        for _ in 0..k {
            let mut node = rest.expect("counted k nodes");
            rest = node.next.take();
            node.next = group;
            group = Some(node);
        }
        *slot = group;
        for _ in 0..k {
            slot = &mut slot.as_mut().expect("k nodes in the group").next;
        }
        *slot = rest;
    }
    head
}

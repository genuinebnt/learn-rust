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

fn len(mut node: &Option<Box<ListNode>>) -> usize {
    let mut n = 0;
    while let Some(x) = node {
        n += 1;
        node = &x.next;
    }
    n
}

pub fn reorder(head: &mut Option<Box<ListNode>>) {
    // Repeatedly detach the last node and insert it after the current one.
    let mut cur = head.as_mut();
    while let Some(node) = cur {
        if node.next.as_ref().is_none_or(|n| n.next.is_none()) {
            break;
        }
        let mut last = &mut node.next;
        while last.as_ref().is_some_and(|n| n.next.is_some()) {
            last = &mut last.as_mut().expect("checked").next;
        }
        let mut tail = last.take().expect("at least two nodes follow");
        tail.next = node.next.take();
        node.next = Some(tail);
        cur = node.next.as_mut().expect("just inserted").next.as_mut();
    }
}

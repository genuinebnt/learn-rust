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

pub fn remove_nth_from_end(mut head: Option<Box<ListNode>>, n: usize) -> Option<Box<ListNode>> {
    let len = len(&head);
    if n == 0 || n > len {
        return head;
    }
    let mut cur = &mut head;
    for _ in 0..len - n {
        cur = &mut cur.as_mut().expect("within the length").next;
    }
    if let Some(node) = cur.as_mut() {
        node.next = node.next.take().and_then(|next| next.next);
    }
    head
}

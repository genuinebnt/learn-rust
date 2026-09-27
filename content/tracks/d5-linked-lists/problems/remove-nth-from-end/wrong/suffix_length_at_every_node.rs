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
    // Step forward until the rest of the list is exactly n long.
    let mut cur = &mut head;
    while cur.is_some() && len(cur) != n {
        cur = &mut cur.as_mut().expect("checked").next;
    }
    if n > 0 && cur.is_some() {
        *cur = cur.take().and_then(|node| node.next);
    }
    head
}

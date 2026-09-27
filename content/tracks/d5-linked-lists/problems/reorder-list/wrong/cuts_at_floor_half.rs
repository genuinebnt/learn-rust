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

fn reverse(head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    let (mut prev, mut cur) = (None, head);
    while let Some(mut node) = cur {
        cur = node.next.take();
        node.next = prev;
        prev = Some(node);
    }
    prev
}

pub fn reorder(head: &mut Option<Box<ListNode>>) {
    let n = len(head);
    if n < 3 {
        return;
    }
    let mut cut = &mut *head;
    for _ in 0..n / 2 {
        cut = &mut cut.as_mut().expect("within the length").next;
    }
    let mut back = reverse(cut.take());
    let mut front = head.as_mut();
    while let (Some(f), Some(mut b)) = (front, back) {
        back = b.next.take();
        b.next = f.next.take();
        f.next = Some(b);
        front = f.next.as_mut().expect("just inserted").next.as_mut();
    }
}

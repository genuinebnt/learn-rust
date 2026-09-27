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

pub fn is_palindrome(mut head: Option<Box<ListNode>>) -> bool {
    let n = len(&head);
    let mut cut = &mut head;
    for _ in 0..n / 2 {
        cut = &mut cut.as_mut().expect("within the length").next;
    }
    let back = cut.take();
    let (mut f, mut b) = (head.as_deref(), back.as_deref());
    while let (Some(x), Some(y)) = (f, b) {
        if x.val != y.val {
            return false;
        }
        f = x.next.as_deref();
        b = y.next.as_deref();
    }
    true
}

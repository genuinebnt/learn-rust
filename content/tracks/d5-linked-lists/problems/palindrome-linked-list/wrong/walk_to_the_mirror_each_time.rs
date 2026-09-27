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

pub fn is_palindrome(head: Option<Box<ListNode>>) -> bool {
    // Compare node i with node n - 1 - i, walking from the head to find each one.
    let n = len(&head);
    let nth = |mut i: usize| {
        let mut cur = head.as_deref();
        while i > 0 {
            cur = cur.and_then(|c| c.next.as_deref());
            i -= 1;
        }
        cur.map(|c| c.val)
    };
    (0..n / 2).all(|i| nth(i) == nth(n - 1 - i))
}

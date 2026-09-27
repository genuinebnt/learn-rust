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

pub fn add_two_numbers(a: Option<Box<ListNode>>, b: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    fn go(a: Option<Box<ListNode>>, b: Option<Box<ListNode>>, carry: i32) -> Option<Box<ListNode>> {
        if a.is_none() && b.is_none() && carry == 0 {
            return None;
        }
        let (av, an) = a.map_or((0, None), |n| (n.val, n.next));
        let (bv, bn) = b.map_or((0, None), |n| (n.val, n.next));
        let sum = av + bv + carry;
        Some(Box::new(ListNode { val: sum % 10, next: go(an, bn, sum / 10) }))
    }
    go(a, b, 0)
}

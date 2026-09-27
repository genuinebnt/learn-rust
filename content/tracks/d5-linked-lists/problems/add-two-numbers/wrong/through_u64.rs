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
    let num = |l: &Option<Box<ListNode>>| values(l).iter().rev().fold(0u64, |acc, &d| acc * 10 + d as u64);
    let mut sum = num(&a) + num(&b);
    let mut digits = vec![(sum % 10) as i32];
    sum /= 10;
    while sum > 0 {
        digits.push((sum % 10) as i32);
        sum /= 10;
    }
    if a.is_none() && b.is_none() {
        return None;
    }
    list(&digits)
}

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

pub fn add_two_numbers(mut a: Option<Box<ListNode>>, mut b: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    let mut head = None;
    let mut tail = &mut head;
    let mut carry = 0;
    while a.is_some() || b.is_some() {
        let mut sum = carry;
        if let Some(node) = a {
            sum += node.val;
            a = node.next;
        }
        if let Some(node) = b {
            sum += node.val;
            b = node.next;
        }
        carry = sum / 10;
        tail = &mut tail.insert(Box::new(ListNode { val: sum % 10, next: None })).next;
    }
    head
}

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

use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn merge_k(mut lists: Vec<Option<Box<ListNode>>>) -> Option<Box<ListNode>> {
    let mut head = None;
    let mut tail = &mut head;
    loop {
        // Find the list with the smallest front by looking at every list.
        let mut best: Option<usize> = None;
        for i in 0..lists.len() {
            if let Some(n) = &lists[i] {
                if best.is_none_or(|b| n.val < lists[b].as_ref().expect("non-empty").val) {
                    best = Some(i);
                }
            }
        }
        let Some(i) = best else { break };
        let mut node = lists[i].take().expect("non-empty");
        lists[i] = node.next.take();
        tail = &mut tail.insert(node).next;
    }
    head
}

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

pub fn merge_k(lists: Vec<Option<Box<ListNode>>>) -> Option<Box<ListNode>> {
    // Sort the list heads, then chain them.
    let mut heads: Vec<Box<ListNode>> = lists.into_iter().flatten().collect();
    heads.sort_by_key(|n| Reverse(n.val));
    let mut out = None;
    for mut node in heads {
        node.next = out;
        out = Some(node);
    }
    out
}

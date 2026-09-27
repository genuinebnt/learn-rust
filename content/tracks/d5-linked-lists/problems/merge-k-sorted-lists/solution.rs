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
    // (front value, list index): the heap never holds nodes, only which list to take from.
    let mut heap: BinaryHeap<Reverse<(i32, usize)>> =
        lists.iter().enumerate().filter_map(|(i, l)| l.as_ref().map(|n| Reverse((n.val, i)))).collect();
    let mut head = None;
    let mut tail = &mut head;
    while let Some(Reverse((_, i))) = heap.pop() {
        let mut node = lists[i].take().expect("the heap only names non-empty lists");
        lists[i] = node.next.take();
        if let Some(n) = &lists[i] {
            heap.push(Reverse((n.val, i)));
        }
        tail = &mut tail.insert(node).next;
    }
    head
}

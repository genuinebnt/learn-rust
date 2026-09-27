from author import T, prob, write_track

# LeetCode's list shape plus two helpers, shared by most problems (given in both starter and solution).
LIST = """
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
"""

REVERSE_HELPER = """
fn reverse(head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    let (mut prev, mut cur) = (None, head);
    while let Some(mut node) = cur {
        cur = node.next.take();
        node.next = prev;
        prev = Some(node);
    }
    prev
}
"""

LEN_HELPER = """
fn len(mut node: &Option<Box<ListNode>>) -> usize {
    let mut n = 0;
    while let Some(x) = node {
        n += 1;
        node = &x.next;
    }
    n
}
"""


def with_list(body: str, extra: str = "") -> str:
    return LIST.strip("\n") + "\n" + extra + "\n" + body.strip("\n") + "\n"


# For hidden tests with long lists: the default drop of a Box chain recurses once per node.
FREE = """
/// Drops a long list one node at a time (the default drop recurses once per node).
fn free(mut l: Option<Box<ListNode>>) {
    while let Some(mut n) = l {
        l = n.next.take();
    }
}
"""


P = []

# ---------------------------------------------------------------- owned lists (easy)

P.append(prob(
    "reverse-linked-list", "Reverse a linked list", "easy", "owned-lists", ["Option<Box<_>>", "take", "Blind 75"],
    "Reverse the list and return the new head. No recursion: the hidden tests have 10⁵ nodes.",
    with_list("""
pub fn reverse(head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    todo!()
}
"""),
    with_list("""
pub fn reverse(head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    let (mut prev, mut cur) = (None, head);
    while let Some(mut node) = cur {
        // Detach the rest, point this node back, and move on.
        cur = node.next.take();
        node.next = prev;
        prev = Some(node);
    }
    prev
}
"""),
    [T("five", "[1,2,3,4,5]", "values(&reverse(list(&[1, 2, 3, 4, 5])))", "vec![5, 4, 3, 2, 1]"),
     T("two", "[1,2]", "values(&reverse(list(&[1, 2])))", "vec![2, 1]"),
     T("empty", "[]", "reverse(None)", "None"),
     T("single", "[7]", "values(&reverse(list(&[7])))", "vec![7]"),
     T("duplicates", "[1,1,2]", "values(&reverse(list(&[1, 1, 2])))", "vec![2, 1, 1]")],
    [T("empty", "[]", "reverse(None)", "None"),
     T("long", "10⁴ nodes", "values(&reverse(list(&v))) == v.iter().rev().copied().collect::<Vec<_>>()", "true", setup="let v: Vec<i32> = (0..10_000).collect();"),
     T("single", "[7]", "values(&reverse(list(&[7])))", "vec![7]"),
     T("three", "[1,2,3]", "values(&reverse(list(&[1, 2, 3])))", "vec![3, 2, 1]"),
     T("extremes", "[i32::MIN, 0, i32::MAX]", "values(&reverse(list(&[i32::MIN, 0, i32::MAX])))", "vec![i32::MAX, 0, i32::MIN]"),
     T("all_same", "[4,4,4]", "values(&reverse(list(&[4, 4, 4])))", "vec![4, 4, 4]"),
     T("twice_is_identity", "[3,1,2] reversed twice", "values(&reverse(reverse(list(&[3, 1, 2]))))", "vec![3, 1, 2]"),
     T("negatives", "[-1,-2,-3,-4]", "values(&reverse(list(&[-1, -2, -3, -4])))", "vec![-4, -3, -2, -1]"),
     FREE,
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(501);
         for _ in 0..300 {
             let n = rng.below(12);
             let v: Vec<i32> = rng.vec(n, -9, 9);
             let want: Vec<i32> = v.iter().rev().copied().collect();
             check!(format!("{v:?}"), values(&reverse(list(&v))), want);
         }
     }

     #[test]
     fn scale_100k() {
         let v: Vec<i32> = (0..100_000).collect();
         let r = reverse(list(&v));
         let got = values(&r);
         free(r);
         check!("0..100000", (got.len(), got[0], got[99_999]), (100_000, 99_999, 0));
     }
     """],
    [("rust", "`while let Some(mut node) = cur` takes ownership of one box at a time."),
     ("rust", "`node.next.take()` moves the rest of the list out and leaves `None` behind, so the node can be relinked.")],
    ("Each iteration owns exactly one node, so the borrow checker has nothing to object to. `take()` is how you move out of a field you still need to write to.", "O(n)", "O(1)"),
    "Write the recursive version. What limits how long a list it can handle?",
    ["Moving boxes between `Option`s with `take()`."],
    examples=[("[1,2,3,4,5]", "[5,4,3,2,1]")],
    constraints=["0 ≤ list length ≤ 10⁵"],
    wrong=dict(
        recursive=with_list("""
pub fn reverse(head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    fn go(node: Option<Box<ListNode>>, acc: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
        match node {
            None => acc,
            Some(mut n) => {
                let rest = n.next.take();
                n.next = acc;
                go(rest, Some(n))
            }
        }
    }
    go(head, None)
}
"""),
        move_the_tail_each_time=with_list("""
pub fn reverse(mut head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    let mut out = None;
    let mut tail = &mut out;
    while head.is_some() {
        // Walk to the last node, detach it and append it to the output.
        let mut cur = &mut head;
        while cur.as_ref().is_some_and(|n| n.next.is_some()) {
            cur = &mut cur.as_mut().expect("checked").next;
        }
        let node = cur.take().expect("the list isn't empty");
        tail = &mut tail.insert(node).next;
    }
    out
}
"""),
        drops_the_first_node=with_list("""
pub fn reverse(head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    let mut prev = None;
    let mut cur = head.and_then(|h| h.next);
    while let Some(mut node) = cur {
        cur = node.next.take();
        node.next = prev;
        prev = Some(node);
    }
    prev
}
"""),
    ),
))

P.append(prob(
    "merge-two-sorted-lists", "Merge two sorted lists", "easy", "owned-lists", ["tail cursor", "Option::insert", "Blind 75"],
    "Merge two sorted lists into one sorted list by relinking their nodes (no new nodes).",
    with_list("""
pub fn merge(a: Option<Box<ListNode>>, b: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    todo!()
}
"""),
    with_list("""
pub fn merge(mut a: Option<Box<ListNode>>, mut b: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    let mut head = None;
    // Where the next node goes: always the `next` of the last node placed.
    let mut tail = &mut head;
    while let (Some(x), Some(y)) = (&a, &b) {
        let src = if x.val <= y.val { &mut a } else { &mut b };
        let mut node = src.take().expect("checked by the loop condition");
        *src = node.next.take();
        tail = &mut tail.insert(node).next;
    }
    *tail = a.or(b);
    head
}
"""),
    [T("interleave", "[1,2,4] + [1,3,4]", "values(&merge(list(&[1, 2, 4]), list(&[1, 3, 4])))", "vec![1, 1, 2, 3, 4, 4]"),
     T("one_empty", "[] + [0]", "values(&merge(None, list(&[0])))", "vec![0]"),
     T("both_empty", "[] + []", "merge(None, None)", "None"),
     T("disjoint", "[5,6] + [1,2]", "values(&merge(list(&[5, 6]), list(&[1, 2])))", "vec![1, 2, 5, 6]"),
     T("uneven_lengths", "[1] + [2,3,4]", "values(&merge(list(&[1]), list(&[2, 3, 4])))", "vec![1, 2, 3, 4]")],
    [T("both_empty", "[] + []", "merge(None, None)", "None"),
     T("disjoint", "[5,6] + [1,2]", "values(&merge(list(&[5, 6]), list(&[1, 2])))", "vec![1, 2, 5, 6]"),
     T("long", "odds + evens below 10⁴", "values(&merge(list(&odd), list(&even))) == (0..10_000).collect::<Vec<_>>()", "true",
       setup="let odd: Vec<i32> = (0..10_000).filter(|x| x % 2 == 1).collect();\nlet even: Vec<i32> = (0..10_000).filter(|x| x % 2 == 0).collect();"),
     T("second_empty", "[1,2] + []", "values(&merge(list(&[1, 2]), None))", "vec![1, 2]"),
     T("all_equal", "[3,3] + [3,3,3]", "values(&merge(list(&[3, 3]), list(&[3, 3, 3])))", "vec![3, 3, 3, 3, 3]"),
     T("negatives", "[-5,-1] + [-3,0]", "values(&merge(list(&[-5, -1]), list(&[-3, 0])))", "vec![-5, -3, -1, 0]"),
     T("extremes", "[i32::MIN, i32::MAX] + [0]", "values(&merge(list(&[i32::MIN, i32::MAX]), list(&[0])))", "vec![i32::MIN, 0, i32::MAX]"),
     T("rest_of_first", "[1,5,6,7] + [2]", "values(&merge(list(&[1, 5, 6, 7]), list(&[2])))", "vec![1, 2, 5, 6, 7]"),
     FREE,
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(502);
         for _ in 0..300 {
             let (m, n) = (rng.below(8), rng.below(8));
             let mut a: Vec<i32> = rng.vec(m, -9, 9);
             let mut b: Vec<i32> = rng.vec(n, -9, 9);
             a.sort();
             b.sort();
             let mut want = [a.clone(), b.clone()].concat();
             want.sort();
             check!(format!("{a:?} + {b:?}"), values(&merge(list(&a), list(&b))), want);
         }
     }

     #[test]
     fn scale_200k() {
         let even: Vec<i32> = (0..200_000).filter(|x| x % 2 == 0).collect();
         let odd: Vec<i32> = (0..200_000).filter(|x| x % 2 == 1).collect();
         let m = merge(list(&even), list(&odd));
         let got = values(&m);
         free(m);
         check!("evens + odds below 200000", got == (0..200_000).collect::<Vec<_>>(), true);
     }
     """],
    [("rust", "Keep `tail: &mut Option<Box<ListNode>>`, the empty slot where the next node goes. `tail.insert(node)` fills it and returns the node."),
     ("rust", "`tail = &mut tail.insert(node).next;` moves the cursor forward. When one list runs out, `*tail = a.or(b)` attaches the rest.")],
    ("A `&mut Option<Box<_>>` cursor replaces the dummy-head trick from other languages. The loop only borrows `a` and `b` long enough to compare.", "O(m + n)", "O(1)"),
    "How would you merge in place if you could only have `&mut` to the lists, not ownership?",
    ["`&mut Option<Box<Node>>` tail cursors.", "`Option::insert` returning `&mut T`."],
    constraints=["0 ≤ total length ≤ 2·10⁵"],
    wrong=dict(
        recursive=with_list("""
pub fn merge(a: Option<Box<ListNode>>, b: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    match (a, b) {
        (None, rest) | (rest, None) => rest,
        (Some(mut x), Some(mut y)) => {
            if x.val <= y.val {
                x.next = merge(x.next.take(), Some(y));
                Some(x)
            } else {
                y.next = merge(Some(x), y.next.take());
                Some(y)
            }
        }
    }
}
"""),
        insert_each_from_the_head=with_list("""
pub fn merge(mut a: Option<Box<ListNode>>, mut b: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    // Insert every node of b into a, searching from the head each time.
    while let Some(mut node) = b {
        b = node.next.take();
        let mut slot = &mut a;
        while slot.as_ref().is_some_and(|n| n.val <= node.val) {
            slot = &mut slot.as_mut().expect("checked").next;
        }
        node.next = slot.take();
        *slot = Some(node);
    }
    a
}
"""),
        forgets_the_rest=with_list("""
pub fn merge(mut a: Option<Box<ListNode>>, mut b: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    let mut head = None;
    let mut tail = &mut head;
    while let (Some(x), Some(y)) = (&a, &b) {
        let src = if x.val <= y.val { &mut a } else { &mut b };
        let mut node = src.take().expect("checked by the loop condition");
        *src = node.next.take();
        tail = &mut tail.insert(node).next;
    }
    if head.is_none() {
        return a.or(b);
    }
    head
}
"""),
    ),
))

P.append(prob(
    "remove-duplicates-from-sorted-list", "Remove duplicates from a sorted list", "easy", "owned-lists", ["as_mut", "and_then"],
    "The list is sorted. Remove nodes so each value appears once, and return the list.",
    with_list("""
pub fn dedup_sorted(head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    todo!()
}
"""),
    with_list("""
pub fn dedup_sorted(mut head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    let mut cur = head.as_mut();
    while let Some(node) = cur {
        while node.next.as_ref().is_some_and(|n| n.val == node.val) {
            // Drop the duplicate and splice in whatever came after it.
            node.next = node.next.take().and_then(|n| n.next);
        }
        cur = node.next.as_mut();
    }
    head
}
"""),
    [T("pairs", "[1,1,2,3,3]", "values(&dedup_sorted(list(&[1, 1, 2, 3, 3])))", "vec![1, 2, 3]"),
     T("none", "[1,2]", "values(&dedup_sorted(list(&[1, 2])))", "vec![1, 2]"),
     T("one_pair", "[1,1,2]", "values(&dedup_sorted(list(&[1, 1, 2])))", "vec![1, 2]"),
     T("empty", "[]", "dedup_sorted(None)", "None"),
     T("all_same", "[7,7,7,7]", "values(&dedup_sorted(list(&[7, 7, 7, 7])))", "vec![7]")],
    [T("all_same", "[7,7,7,7]", "values(&dedup_sorted(list(&[7, 7, 7, 7])))", "vec![7]"),
     T("empty", "[]", "dedup_sorted(None)", "None"),
     T("long", "10⁴ values, each twice", "values(&dedup_sorted(list(&v))).len()", "5_000", setup="let v: Vec<i32> = (0..10_000).map(|i| i / 2).collect();"),
     T("single", "[3]", "values(&dedup_sorted(list(&[3])))", "vec![3]"),
     T("dup_at_end", "[1,2,2]", "values(&dedup_sorted(list(&[1, 2, 2])))", "vec![1, 2]"),
     T("negatives", "[-3,-3,-1,0,0]", "values(&dedup_sorted(list(&[-3, -3, -1, 0, 0])))", "vec![-3, -1, 0]"),
     T("extremes", "[MIN,MIN,MAX,MAX]", "values(&dedup_sorted(list(&[i32::MIN, i32::MIN, i32::MAX, i32::MAX])))", "vec![i32::MIN, i32::MAX]"),
     T("runs_of_three", "[1,1,1,2,2,2,3]", "values(&dedup_sorted(list(&[1, 1, 1, 2, 2, 2, 3])))", "vec![1, 2, 3]"),
     FREE,
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(503);
         for _ in 0..300 {
             let n = rng.below(12);
             let mut v: Vec<i32> = rng.vec(n, -4, 4);
             v.sort();
             let mut want = v.clone();
             want.dedup();
             check!(format!("{v:?}"), values(&dedup_sorted(list(&v))), want);
         }
     }

     #[test]
     fn scale_200k() {
         let v: Vec<i32> = (0..200_000).collect();
         let l = dedup_sorted(list(&v));
         let got = values(&l);
         free(l);
         check!("0..200000 (no duplicates)", got == v, true);
     }
     """],
    [("rust", "`head.as_mut()` gives `Option<&mut Box<ListNode>>` to walk with, while `head` keeps ownership."),
     ("rust", "`node.next.take().and_then(|n| n.next)` removes one node: the box is dropped, its tail is kept.")],
    ("Only one `&mut` cursor exists at a time, and removing a node is a move out of the box being dropped.", "O(n)", "O(1)"),
    "Remove every value that has duplicates (so [1,1,2] becomes [2]).",
    ["Walking with `as_mut()`.", "Splicing with `take().and_then(..)`."],
    constraints=["0 ≤ list length ≤ 2·10⁵"],
    wrong=dict(
        one_removal_per_node=with_list("""
pub fn dedup_sorted(mut head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    let mut cur = head.as_mut();
    while let Some(node) = cur {
        if node.next.as_ref().is_some_and(|n| n.val == node.val) {
            node.next = node.next.take().and_then(|n| n.next);
        }
        cur = node.next.as_mut();
    }
    head
}
"""),
        drops_every_duplicated_value=with_list("""
pub fn dedup_sorted(head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    let mut out = None;
    let mut tail = &mut out;
    let mut cur = head;
    while let Some(mut node) = cur {
        cur = node.next.take();
        let mut repeated = false;
        while cur.as_ref().is_some_and(|n| n.val == node.val) {
            cur = cur.and_then(|n| n.next);
            repeated = true;
        }
        if !repeated {
            tail = &mut tail.insert(node).next;
        }
    }
    out
}
"""),
        seen_list_scan=with_list("""
pub fn dedup_sorted(head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    // Works for unsorted input too: keep a node only if its value hasn't been kept yet.
    let mut seen: Vec<i32> = Vec::new();
    let mut out = None;
    let mut tail = &mut out;
    let mut cur = head;
    while let Some(mut node) = cur {
        cur = node.next.take();
        if !seen.contains(&node.val) {
            seen.push(node.val);
            tail = &mut tail.insert(node).next;
        }
    }
    out
}
"""),
    ),
))

P.append(prob(
    "middle-of-the-list", "Middle of the list", "easy", "owned-lists", ["as_deref", "slow/fast"],
    "Return a reference to the middle node; for an even length, the second of the two middle nodes.",
    with_list("""
pub fn middle(head: &Option<Box<ListNode>>) -> Option<&ListNode> {
    todo!()
}
"""),
    with_list("""
pub fn middle(head: &Option<Box<ListNode>>) -> Option<&ListNode> {
    let (mut slow, mut fast) = (head.as_deref(), head.as_deref());
    while let Some(f) = fast.and_then(|f| f.next.as_deref()) {
        slow = slow.and_then(|s| s.next.as_deref());
        fast = f.next.as_deref();
    }
    slow
}
"""),
    [T("odd", "[1,2,3,4,5]", "middle(&l).map(|n| n.val)", "Some(3)", setup="let l = list(&[1, 2, 3, 4, 5]);"),
     T("even", "[1,2,3,4,5,6]", "middle(&l).map(|n| n.val)", "Some(4)", setup="let l = list(&[1, 2, 3, 4, 5, 6]);"),
     T("single", "[9]", "middle(&l).map(|n| n.val)", "Some(9)", setup="let l = list(&[9]);"),
     T("two", "[1,2]", "middle(&l).map(|n| n.val)", "Some(2)", setup="let l = list(&[1, 2]);"),
     T("empty", "[]", "middle(&None).is_none()", "true")],
    [T("single", "[9]", "middle(&l).map(|n| n.val)", "Some(9)", setup="let l = list(&[9]);"),
     T("empty", "[]", "middle(&None).is_none()", "true"),
     T("two", "[1,2]", "middle(&l).map(|n| n.val)", "Some(2)", setup="let l = list(&[1, 2]);"),
     T("three", "[1,2,3]", "middle(&l).map(|n| n.val)", "Some(2)", setup="let l = list(&[1, 2, 3]);"),
     T("four", "[1,2,3,4]", "middle(&l).map(|n| n.val)", "Some(3)", setup="let l = list(&[1, 2, 3, 4]);"),
     T("rest_is_attached", "[1,2,3,4,5]: values from the middle on", "values(&middle(&l).unwrap().next)", "vec![4, 5]", setup="let l = list(&[1, 2, 3, 4, 5]);"),
     T("same_node", "[5,5,5,5]: the middle is the third node itself", "std::ptr::eq(middle(&l).unwrap(), l.as_ref().unwrap().next.as_ref().unwrap().next.as_deref().unwrap())", "true",
       setup="let l = list(&[5, 5, 5, 5]);"),
     T("long_even", "10⁴ nodes", "middle(&l).map(|n| n.val)", "Some(5_000)", setup="let l = list(&(0..10_000).collect::<Vec<i32>>());"),
     FREE,
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(504);
         for _ in 0..300 {
             let n = rng.below(12);
             let v: Vec<i32> = rng.vec(n, -9, 9);
             let l = list(&v);
             check!(format!("{v:?}"), middle(&l).map(|m| values(&Some(Box::new(m.clone())))), (n > 0).then(|| v[n / 2..].to_vec()));
         }
     }

     #[test]
     fn scale_200k() {
         let l = list(&(0..200_000).collect::<Vec<i32>>());
         let got = middle(&l).map(|n| n.val);
         free(l);
         check!("0..200000", got, Some(100_000));
     }
     """],
    [("rust", "`as_deref()` turns `&Option<Box<ListNode>>` into `Option<&ListNode>`, which is `Copy`: easy to move two pointers around."),
     ("approach", "Move one reference one step and another two steps; when the fast one runs out, the slow one is in the middle.")],
    ("Shared references are `Copy`, so slow/fast pointers work exactly as in other languages once you're holding `Option<&ListNode>`.", "O(n)", "O(1)"),
    "Return a `&mut ListNode` instead. What changes, and why can't you keep two `&mut` cursors?",
    ["`Option::as_deref` for reading lists.", "Slow/fast pointers with shared references."],
    constraints=["0 ≤ list length ≤ 2·10⁵"],
    wrong=dict(
        first_middle_on_even=with_list("""
pub fn middle(head: &Option<Box<ListNode>>) -> Option<&ListNode> {
    let (mut slow, mut fast) = (head.as_deref(), head.as_deref());
    while let Some(f) = fast.and_then(|f| f.next.as_deref()).and_then(|f| f.next.as_deref()) {
        slow = slow.and_then(|s| s.next.as_deref());
        fast = Some(f);
    }
    slow
}
"""),
        one_step_too_far=with_list("""
pub fn middle(head: &Option<Box<ListNode>>) -> Option<&ListNode> {
    let (mut slow, mut fast) = (head.as_deref(), head.as_deref());
    while let Some(f) = fast {
        slow = slow.and_then(|s| s.next.as_deref());
        fast = f.next.as_deref().and_then(|f| f.next.as_deref());
    }
    slow
}
"""),
    ),
))

P.append(prob(
    "fix-move-out-of-borrowed-box", "Fix: move out of a borrowed Box", "easy", "owned-lists", ["E0507", "take"],
    "`pop_front` should remove the first node and return its value. It doesn't compile.",
    with_list("""
/// Removes the first node and returns its value.
pub fn pop_front(head: &mut Option<Box<ListNode>>) -> Option<i32> {
    match head {
        Some(node) => {
            *head = node.next;
            Some(node.val)
        }
        None => None,
    }
}

pub fn push_front(head: &mut Option<Box<ListNode>>, val: i32) {
    let next = head.take();
    *head = Some(Box::new(ListNode { val, next }));
}
"""),
    with_list("""
/// Removes the first node and returns its value.
pub fn pop_front(head: &mut Option<Box<ListNode>>) -> Option<i32> {
    let node = head.take()?;
    *head = node.next;
    Some(node.val)
}

pub fn push_front(head: &mut Option<Box<ListNode>>, val: i32) {
    let next = head.take();
    *head = Some(Box::new(ListNode { val, next }));
}
"""),
    [T("pops", "[1,2,3]; pop twice", "(pop_front(&mut l), pop_front(&mut l), values(&l))", "(Some(1), Some(2), vec![3])", setup="let mut l = list(&[1, 2, 3]);"),
     T("empty", "[]; pop", "pop_front(&mut None)", "None"),
     T("single", "[9]; pop", "(pop_front(&mut l), l)", "(Some(9), None)", setup="let mut l = list(&[9]);"),
     T("push_then_pop", "push 5 onto [1]; pop", "{ push_front(&mut l, 5); (pop_front(&mut l), values(&l)) }", "(Some(5), vec![1])", setup="let mut l = list(&[1]);"),
     T("drain", "[4,5]; pop three times", "(pop_front(&mut l), pop_front(&mut l), pop_front(&mut l), l)", "(Some(4), Some(5), None, None)", setup="let mut l = list(&[4, 5]);")],
    [T("push_then_pop", "push 5 onto [1]; pop", "{ push_front(&mut l, 5); (pop_front(&mut l), values(&l)) }", "(Some(5), vec![1])", setup="let mut l = list(&[1]);"),
     T("drain", "[4,5]; pop three times", "(pop_front(&mut l), pop_front(&mut l), pop_front(&mut l), l)", "(Some(4), Some(5), None, None)", setup="let mut l = list(&[4, 5]);"),
     T("push_onto_empty", "push 3 onto []; pop", "{ push_front(&mut l, 3); (pop_front(&mut l), l) }", "(Some(3), None)", setup="let mut l = None;"),
     T("rest_kept", "[1,2,3,4]; pop once", "(pop_front(&mut l), values(&l))", "(Some(1), vec![2, 3, 4])", setup="let mut l = list(&[1, 2, 3, 4]);"),
     T("extremes", "[i32::MIN, i32::MAX]; pop twice", "(pop_front(&mut l), pop_front(&mut l))", "(Some(i32::MIN), Some(i32::MAX))", setup="let mut l = list(&[i32::MIN, i32::MAX]);"),
     T("stack_order", "push 1, 2, 3; pop three", "{ for x in 1..=3 { push_front(&mut l, x); } (pop_front(&mut l), pop_front(&mut l), pop_front(&mut l)) }", "(Some(3), Some(2), Some(1))",
       setup="let mut l = None;"),
     T("pop_empty_twice", "[]; pop twice", "(pop_front(&mut l), pop_front(&mut l))", "(None, None)", setup="let mut l: Option<Box<ListNode>> = None;"),
     T("drain_10k", "10⁴ nodes; pop all", "{ let mut sum = 0i64; while let Some(v) = pop_front(&mut l) { sum += v as i64; } (sum, l) }", "(49_995_000, None)",
       setup="let mut l = list(&(0..10_000).collect::<Vec<i32>>());"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(505);
         for _ in 0..300 {
             let mut l = None;
             let mut model: Vec<i32> = Vec::new();
             let mut ops = Vec::new();
             for _ in 0..8 {
                 if rng.bool() {
                     let x = rng.int(-9, 9) as i32;
                     push_front(&mut l, x);
                     model.insert(0, x);
                     ops.push(format!("push {x}"));
                 } else {
                     let want = if model.is_empty() { None } else { Some(model.remove(0)) };
                     ops.push("pop".to_string());
                     check!(format!("{ops:?}"), pop_front(&mut l), want);
                 }
                 check!(format!("{ops:?}: list"), values(&l), model.clone());
             }
         }
     }
     """],
    [("rust", "`node` is a `&mut Box<ListNode>` borrowed from `head`. You can't move `node.next` out of something you only borrowed."),
     ("rust", "Take ownership of the whole first node with `head.take()?`; then its fields are yours to move.")],
    ("`take()` swaps `None` into the slot and hands you the owned box, which ends the borrow problem: moving out of an owned `Box` is allowed.", "O(1)", "O(1)"),
    "Why does `Option::take` exist, when it's just `std::mem::replace(slot, None)`?",
    ["Can't move out of a borrow; take ownership first.", "`?` on `Option` for the empty case."],
    mode="fix", rules=dict(methods=["clone", "unwrap"]),
    wrong=dict(
        drops_the_rest=with_list("""
/// Removes the first node and returns its value.
pub fn pop_front(head: &mut Option<Box<ListNode>>) -> Option<i32> {
    let node = head.take()?;
    Some(node.val)
}

pub fn push_front(head: &mut Option<Box<ListNode>>, val: i32) {
    let next = head.take();
    *head = Some(Box::new(ListNode { val, next }));
}
"""),
        peeks_without_removing=with_list("""
/// Removes the first node and returns its value.
pub fn pop_front(head: &mut Option<Box<ListNode>>) -> Option<i32> {
    match head {
        Some(node) => Some(node.val),
        None => None,
    }
}

pub fn push_front(head: &mut Option<Box<ListNode>>, val: i32) {
    let next = head.take();
    *head = Some(Box::new(ListNode { val, next }));
}
"""),
    ),
))

# ---------------------------------------------------------------- cursors (medium)

P.append(prob(
    "remove-nth-from-end", "Remove Nth node from end", "medium", "cursors", ["&mut cursor", "Blind 75"],
    """
    Remove the `n`-th node from the end (`n = 1` is the last node) and return the list. If `n` is 0 or longer
    than the list, return it unchanged.
    """,
    with_list("""
pub fn remove_nth_from_end(head: Option<Box<ListNode>>, n: usize) -> Option<Box<ListNode>> {
    todo!()
}
"""),
    with_list("""
pub fn remove_nth_from_end(mut head: Option<Box<ListNode>>, n: usize) -> Option<Box<ListNode>> {
    let len = len(&head);
    if n == 0 || n > len {
        return head;
    }
    let mut cur = &mut head;
    for _ in 0..len - n {
        cur = &mut cur.as_mut().expect("within the length").next;
    }
    *cur = cur.take().and_then(|node| node.next);
    head
}
""", LEN_HELPER),
    [T("middle", "[1,2,3,4,5], n = 2", "values(&remove_nth_from_end(list(&[1, 2, 3, 4, 5]), 2))", "vec![1, 2, 3, 5]"),
     T("only", "[1], n = 1", "remove_nth_from_end(list(&[1]), 1)", "None"),
     T("last", "[1,2], n = 1", "values(&remove_nth_from_end(list(&[1, 2]), 1))", "vec![1]"),
     T("first", "[1,2], n = 2", "values(&remove_nth_from_end(list(&[1, 2]), 2))", "vec![2]"),
     T("out_of_range", "[1,2], n = 3 and 0", "(values(&remove_nth_from_end(list(&[1, 2]), 3)), values(&remove_nth_from_end(list(&[1, 2]), 0)))", "(vec![1, 2], vec![1, 2])")],
    [T("last", "[1,2], n = 1", "values(&remove_nth_from_end(list(&[1, 2]), 1))", "vec![1]"),
     T("first", "[1,2], n = 2", "values(&remove_nth_from_end(list(&[1, 2]), 2))", "vec![2]"),
     T("out_of_range", "[1,2], n = 3 and 0", "(values(&remove_nth_from_end(list(&[1, 2]), 3)), values(&remove_nth_from_end(list(&[1, 2]), 0)))", "(vec![1, 2], vec![1, 2])"),
     T("empty", "[], n = 1", "remove_nth_from_end(None, 1)", "None"),
     T("head_of_long", "[1..=5], n = 5", "values(&remove_nth_from_end(list(&[1, 2, 3, 4, 5]), 5))", "vec![2, 3, 4, 5]"),
     T("last_of_long", "[1..=5], n = 1", "values(&remove_nth_from_end(list(&[1, 2, 3, 4, 5]), 1))", "vec![1, 2, 3, 4]"),
     T("huge_n", "[1,2,3], n = usize::MAX", "values(&remove_nth_from_end(list(&[1, 2, 3]), usize::MAX))", "vec![1, 2, 3]"),
     T("duplicates", "[7,7,7], n = 2", "values(&remove_nth_from_end(list(&[7, 7, 7]), 2))", "vec![7, 7]"),
     FREE,
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(506);
         for _ in 0..300 {
             let len = rng.below(8);
             let v: Vec<i32> = (0..len as i32).collect();
             let n = rng.below(10);
             let mut want = v.clone();
             if n >= 1 && n <= len {
                 want.remove(len - n);
             }
             check!(format!("{v:?}, n = {n}"), values(&remove_nth_from_end(list(&v), n)), want);
         }
     }

     #[test]
     fn scale_200k() {
         let v: Vec<i32> = (0..200_000).collect();
         let l = remove_nth_from_end(list(&v), 1);
         let got = values(&l);
         free(l);
         check!("0..200000, n = 1", (got.len(), got[199_998]), (199_999, 199_998));
     }
     """],
    [("approach", "In Rust the two-pointer trick needs two cursors into the same list at once. Counting first, then walking once with a single `&mut`, is simpler."),
     ("rust", "`cur = &mut cur.as_mut().expect(..).next;` steps a `&mut Option<Box<_>>` cursor forward. Then `*cur = cur.take().and_then(|n| n.next)` unlinks.")],
    ("Two passes, but only one mutable cursor, which is the shape the borrow checker likes. Pointing at the slot (not the node before it) removes the need for a dummy head.", "O(n)", "O(1)"),
    "Do it in one pass. What would you have to give up or use (e.g. indices, `unsafe`)?",
    ["Stepping a `&mut Option<Box<_>>` cursor.", "Removing through the slot, not the previous node."],
    constraints=["0 ≤ list length ≤ 2·10⁵"],
    wrong=dict(
        counts_from_the_front=with_list("""
pub fn remove_nth_from_end(mut head: Option<Box<ListNode>>, n: usize) -> Option<Box<ListNode>> {
    let len = len(&head);
    if n == 0 || n > len {
        return head;
    }
    let mut cur = &mut head;
    for _ in 0..n - 1 {
        cur = &mut cur.as_mut().expect("within the length").next;
    }
    *cur = cur.take().and_then(|node| node.next);
    head
}
""", LEN_HELPER),
        off_by_one=with_list("""
pub fn remove_nth_from_end(mut head: Option<Box<ListNode>>, n: usize) -> Option<Box<ListNode>> {
    let len = len(&head);
    if n == 0 || n > len {
        return head;
    }
    let mut cur = &mut head;
    for _ in 0..len - n {
        cur = &mut cur.as_mut().expect("within the length").next;
    }
    if let Some(node) = cur.as_mut() {
        node.next = node.next.take().and_then(|next| next.next);
    }
    head
}
""", LEN_HELPER),
        suffix_length_at_every_node=with_list("""
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
""", LEN_HELPER),
    ),
))

P.append(prob(
    "reorder-list", "Reorder list", "medium", "cursors", ["split", "reverse", "interleave", "Blind 75"],
    "Reorder L0 → L1 → … → Ln into L0 → Ln → L1 → Ln−1 → …, in place, by relinking nodes.",
    with_list("""
pub fn reorder(head: &mut Option<Box<ListNode>>) {
    todo!()
}
"""),
    with_list("""
pub fn reorder(head: &mut Option<Box<ListNode>>) {
    let n = len(head);
    if n < 3 {
        return;
    }
    // Cut after the first ceil(n / 2) nodes and reverse the rest.
    let mut cut = &mut *head;
    for _ in 0..n.div_ceil(2) {
        cut = &mut cut.as_mut().expect("within the length").next;
    }
    let mut back = reverse(cut.take());
    // Splice one node from the back half after each node of the front half.
    let mut front = head.as_mut();
    while let (Some(f), Some(mut b)) = (front, back) {
        back = b.next.take();
        b.next = f.next.take();
        f.next = Some(b);
        front = f.next.as_mut().expect("just inserted").next.as_mut();
    }
}
""", LEN_HELPER + REVERSE_HELPER),
    [T("even", "[1,2,3,4]", "{ reorder(&mut l); values(&l) }", "vec![1, 4, 2, 3]", setup="let mut l = list(&[1, 2, 3, 4]);"),
     T("odd", "[1,2,3,4,5]", "{ reorder(&mut l); values(&l) }", "vec![1, 5, 2, 4, 3]", setup="let mut l = list(&[1, 2, 3, 4, 5]);"),
     T("empty", "[]", "{ reorder(&mut l); l }", "None", setup="let mut l = None;"),
     T("short", "[1,2]", "{ reorder(&mut l); values(&l) }", "vec![1, 2]", setup="let mut l = list(&[1, 2]);"),
     T("three", "[1,2,3]", "{ reorder(&mut l); values(&l) }", "vec![1, 3, 2]", setup="let mut l = list(&[1, 2, 3]);")],
    [T("short", "[1,2]", "{ reorder(&mut l); values(&l) }", "vec![1, 2]", setup="let mut l = list(&[1, 2]);"),
     T("empty", "[]", "{ reorder(&mut l); l }", "None", setup="let mut l = None;"),
     T("long", "10⁴ nodes: first and last swap in", "{ reorder(&mut l); values(&l)[..4].to_vec() }", "vec![0, 9_999, 1, 9_998]", setup="let mut l = list(&(0..10_000).collect::<Vec<_>>());"),
     T("single", "[1]", "{ reorder(&mut l); values(&l) }", "vec![1]", setup="let mut l = list(&[1]);"),
     T("six", "[1..=6]", "{ reorder(&mut l); values(&l) }", "vec![1, 6, 2, 5, 3, 4]", setup="let mut l = list(&[1, 2, 3, 4, 5, 6]);"),
     T("seven", "[1..=7]", "{ reorder(&mut l); values(&l) }", "vec![1, 7, 2, 6, 3, 5, 4]", setup="let mut l = list(&[1, 2, 3, 4, 5, 6, 7]);"),
     T("duplicates", "[2,2,1,1]", "{ reorder(&mut l); values(&l) }", "vec![2, 1, 2, 1]", setup="let mut l = list(&[2, 2, 1, 1]);"),
     T("extremes", "[i32::MIN, 0, i32::MAX]", "{ reorder(&mut l); values(&l) }", "vec![i32::MIN, i32::MAX, 0]", setup="let mut l = list(&[i32::MIN, 0, i32::MAX]);"),
     FREE,
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(507);
         for _ in 0..300 {
             let n = rng.below(12);
             let v: Vec<i32> = rng.vec(n, -9, 9);
             let mut want = Vec::new();
             let (mut i, mut j) = (0, n);
             while i < j {
                 want.push(v[i]);
                 i += 1;
                 if i < j {
                     j -= 1;
                     want.push(v[j]);
                 }
             }
             let mut l = list(&v);
             reorder(&mut l);
             check!(format!("{v:?}"), values(&l), want);
         }
     }

     #[test]
     fn scale_200k() {
         let mut l = list(&(0..200_000).collect::<Vec<i32>>());
         reorder(&mut l);
         let got = values(&l);
         free(l);
         check!("0..200000", (got.len(), got[0], got[1], got[199_998], got[199_999]), (200_000, 0, 199_999, 99_999, 100_000));
     }
     """],
    [("approach", "Three steps: cut the list in half, reverse the back half, then interleave."),
     ("rust", "The interleave loop owns `back` and walks `front` as `Option<&mut Box<ListNode>>`; both are reassigned every iteration."),
     ("edge case", "Cut after ceil(n/2) nodes so the front half is never shorter than the back half.")],
    ("Each step is a small, borrow-friendly loop. The alternative, collecting nodes into a Vec, costs O(n) space.", "O(n)", "O(1)"),
    "Undo the reordering (restore the original order) in O(1) space.",
    ["Splitting a list at a `&mut` cursor with `take()`.", "Interleaving an owned list into a borrowed one."],
    constraints=["0 ≤ list length ≤ 2·10⁵"],
    wrong=dict(
        move_the_tail_each_time=with_list("""
pub fn reorder(head: &mut Option<Box<ListNode>>) {
    // Repeatedly detach the last node and insert it after the current one.
    let mut cur = head.as_mut();
    while let Some(node) = cur {
        if node.next.as_ref().is_none_or(|n| n.next.is_none()) {
            break;
        }
        let mut last = &mut node.next;
        while last.as_ref().is_some_and(|n| n.next.is_some()) {
            last = &mut last.as_mut().expect("checked").next;
        }
        let mut tail = last.take().expect("at least two nodes follow");
        tail.next = node.next.take();
        node.next = Some(tail);
        cur = node.next.as_mut().expect("just inserted").next.as_mut();
    }
}
""", LEN_HELPER),
        cuts_at_floor_half=with_list("""
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
""", LEN_HELPER + REVERSE_HELPER),
    ),
))

P.append(prob(
    "add-two-numbers", "Add two numbers", "medium", "cursors", ["carry", "tail cursor"],
    """
    Two non-negative numbers are stored as lists of digits, least significant digit first. Return their sum
    in the same form. The numbers can have 10⁵ digits.
    """,
    with_list("""
pub fn add_two_numbers(a: Option<Box<ListNode>>, b: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    todo!()
}
"""),
    with_list("""
pub fn add_two_numbers(mut a: Option<Box<ListNode>>, mut b: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    let mut head = None;
    let mut tail = &mut head;
    let mut carry = 0;
    while a.is_some() || b.is_some() || carry > 0 {
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
"""),
    [T("example", "342 + 465", "values(&add_two_numbers(list(&[2, 4, 3]), list(&[5, 6, 4])))", "vec![7, 0, 8]"),
     T("zeros", "0 + 0", "values(&add_two_numbers(list(&[0]), list(&[0])))", "vec![0]"),
     T("carry_out", "9999999 + 9999", "values(&add_two_numbers(list(&[9, 9, 9, 9, 9, 9, 9]), list(&[9, 9, 9, 9])))", "vec![8, 9, 9, 9, 0, 0, 0, 1]"),
     T("final_carry", "5 + 5", "values(&add_two_numbers(list(&[5]), list(&[5])))", "vec![0, 1]"),
     T("both_empty", "[] + []", "add_two_numbers(None, None)", "None")],
    [T("carry_out", "9999999 + 9999", "values(&add_two_numbers(list(&[9, 9, 9, 9, 9, 9, 9]), list(&[9, 9, 9, 9])))", "vec![8, 9, 9, 9, 0, 0, 0, 1]"),
     T("final_carry", "5 + 5", "values(&add_two_numbers(list(&[5]), list(&[5])))", "vec![0, 1]"),
     T("second_longer", "12 + 99921", "values(&add_two_numbers(list(&[2, 1]), list(&[1, 2, 9, 9, 9])))", "vec![3, 3, 9, 9, 9]"),
     T("carry_chain_into_longer", "1 + 999", "values(&add_two_numbers(list(&[1]), list(&[9, 9, 9])))", "vec![0, 0, 0, 1]"),
     T("zero_plus_number", "0 + 507", "values(&add_two_numbers(list(&[0]), list(&[7, 0, 5])))", "vec![7, 0, 5]"),
     T("past_u64", "20 nines + 1", "values(&add_two_numbers(list(&[9; 20]), list(&[1])))", "{ let mut v = vec![0; 20]; v.push(1); v }"),
     FREE,
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(508);
         for _ in 0..300 {
             let (m, n) = (1 + rng.below(9), 1 + rng.below(9));
             let mut a: Vec<i32> = rng.vec(m, 0, 9);
             let mut b: Vec<i32> = rng.vec(n, 0, 9);
             // No leading zeros, except for the number 0 itself.
             if m > 1 {
                 a[m - 1] = rng.int(1, 9) as i32;
             }
             if n > 1 {
                 b[n - 1] = rng.int(1, 9) as i32;
             }
             let num = |d: &[i32]| d.iter().rev().fold(0u64, |acc, &x| acc * 10 + x as u64);
             let mut sum = num(&a) + num(&b);
             let mut want = vec![(sum % 10) as i32];
             sum /= 10;
             while sum > 0 {
                 want.push((sum % 10) as i32);
                 sum /= 10;
             }
             check!(format!("{a:?} + {b:?}"), values(&add_two_numbers(list(&a), list(&b))), want);
         }
     }

     #[test]
     fn scale_100k_digits() {
         let a = list(&vec![9; 100_000]);
         let b = list(&vec![9; 100_000]);
         let s = add_two_numbers(a, b);
         let got = values(&s);
         free(s);
         check!("10⁵ nines + 10⁵ nines", (got.len(), got[0], got[1], got[99_999], got[100_000]), (100_001, 8, 9, 9, 1));
     }
     """,
     T("one_empty", "[] + 12", "values(&add_two_numbers(None, list(&[2, 1])))", "vec![2, 1]"),
     T("huge", "10⁴ nines + 1", "{ let s = values(&add_two_numbers(list(&nines), list(&[1]))); (s.len(), s[0], s[9_999], s[10_000]) }", "(10_001, 0, 0, 1)", setup="let nines = vec![9; 10_000];")],
    [("approach", "Add digit by digit with a carry, like on paper. Keep going while either list or the carry remains."),
     ("rust", "`if let Some(node) = a { …; a = node.next; }` consumes one node and moves the rest back into `a`.")],
    ("Building with a tail cursor keeps digits in order without a dummy head or a final reverse.", "O(max(m, n))", "O(max(m, n))"),
    "The digits come most significant first instead. What changes?",
    ["Consuming two lists in step.", "Building output with a tail cursor."],
    constraints=["0 ≤ digits per number ≤ 10⁵", "no leading zeros, except the number 0"],
    wrong=dict(
        forgets_the_final_carry=with_list("""
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
"""),
        through_u64=with_list("""
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
"""),
        recursive=with_list("""
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
"""),
    ),
))

P.append(prob(
    "palindrome-linked-list", "Palindrome linked list", "medium", "cursors", ["split", "reverse", "as_deref"],
    "Return whether the list's values read the same both ways. Use O(1) extra space: you own the list, so you may relink it.",
    with_list("""
pub fn is_palindrome(head: Option<Box<ListNode>>) -> bool {
    todo!()
}
"""),
    with_list("""
pub fn is_palindrome(mut head: Option<Box<ListNode>>) -> bool {
    let n = len(&head);
    let mut cut = &mut head;
    for _ in 0..n / 2 {
        cut = &mut cut.as_mut().expect("within the length").next;
    }
    // The back half (with the middle node, for odd lengths), reversed.
    let back = reverse(cut.take());
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
""", LEN_HELPER + REVERSE_HELPER),
    [T("even", "[1,2,2,1]", "is_palindrome(list(&[1, 2, 2, 1]))", "true"),
     T("no", "[1,2]", "is_palindrome(list(&[1, 2]))", "false"),
     T("empty", "[]", "is_palindrome(None)", "true"),
     T("single", "[5]", "is_palindrome(list(&[5]))", "true"),
     T("odd", "[1,2,3,2,1]", "is_palindrome(list(&[1, 2, 3, 2, 1]))", "true")],
    [T("odd", "[1,2,3,2,1]", "is_palindrome(list(&[1, 2, 3, 2, 1]))", "true"),
     T("two_same", "[4,4]", "is_palindrome(list(&[4, 4]))", "true"),
     T("middle_differs_even", "[1,3,2,1]", "is_palindrome(list(&[1, 3, 2, 1]))", "false"),
     T("negatives", "[-1,5,-1]", "is_palindrome(list(&[-1, 5, -1]))", "true"),
     T("extremes", "[i32::MIN, i32::MAX, i32::MIN]", "is_palindrome(list(&[i32::MIN, i32::MAX, i32::MIN]))", "true"),
     T("sorted_is_not", "[1,2,3]", "is_palindrome(list(&[1, 2, 3]))", "false"),
     FREE,
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(509);
         for _ in 0..300 {
             let n = rng.below(10);
             let mut v: Vec<i32> = rng.vec(n, 0, 2);
             if rng.bool() {
                 for i in 0..n / 2 {
                     v[n - 1 - i] = v[i];
                 }
             }
             let want = v.iter().eq(v.iter().rev());
             check!(format!("{v:?}"), is_palindrome(list(&v)), want);
         }
     }

     #[test]
     fn scale_200k() {
         let v: Vec<i32> = (0..100_000).chain((0..100_000).rev()).collect();
         let mut w = v.clone();
         w[100_000] = -1;
         // is_palindrome drops the list itself, and a Box chain drops recursively: give it a big stack.
         let got = std::thread::Builder::new()
             .stack_size(512 << 20)
             .spawn(move || (is_palindrome(list(&v)), is_palindrome(list(&w))))
             .expect("spawn")
             .join()
             .expect("is_palindrome panicked");
         check!("0..100000 then back down, and the same with one value changed", got, (true, false));
     }
     """,
     T("empty", "[]", "is_palindrome(None)", "true"),
     T("near_miss", "[1,2,3,1]", "is_palindrome(list(&[1, 2, 3, 1]))", "false"),
     T("long", "10⁴ symmetric values", "is_palindrome(list(&v))", "true", setup="let v: Vec<i32> = (0..5_000).chain((0..5_000).rev()).collect();")],
    [("approach", "Split off the second half, reverse it, and walk both halves together."),
     ("rust", "Taking the list by value is what allows the O(1)-space version: you're free to cut and relink it.")],
    ("Ownership in the signature matters: with `&Option<Box<_>>` you'd have to copy values out (O(n) space) or restore the list afterwards.", "O(n)", "O(1)"),
    "Change the signature to take `&mut Option<Box<ListNode>>` and restore the list before returning.",
    ["How a function's signature decides which algorithms are possible."],
    constraints=["0 ≤ list length ≤ 2·10⁵"],
    wrong=dict(
        walk_to_the_mirror_each_time=with_list("""
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
""", LEN_HELPER),
        forgets_to_reverse=with_list("""
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
""", LEN_HELPER),
        ends_only=with_list("""
pub fn is_palindrome(head: Option<Box<ListNode>>) -> bool {
    let first = head.as_ref().map(|n| n.val);
    let mut last = first;
    let mut cur = head.as_deref();
    while let Some(n) = cur {
        last = Some(n.val);
        cur = n.next.as_deref();
    }
    first == last
}
"""),
    ),
))

P.append(prob(
    "linked-list-cycle", "Linked list cycle (index arena)", "medium", "cursors", ["arena", "Floyd", "Blind 75"],
    """
    `Box` lists can't have cycles, so this list lives in an arena: node `i`'s successor is `next[i]`. Return
    the index where the cycle starts, or `None`. O(1) extra space.
    """,
    """
    /// Where the list starting at `head` enters a cycle, if it has one.
    pub fn cycle_start(next: &[Option<usize>], head: Option<usize>) -> Option<usize> {
        todo!()
    }

    pub fn has_cycle(next: &[Option<usize>], head: Option<usize>) -> bool {
        cycle_start(next, head).is_some()
    }
    """,
    """
    fn step(next: &[Option<usize>], i: Option<usize>) -> Option<usize> {
        i.and_then(|i| next[i])
    }

    /// Where the list starting at `head` enters a cycle, if it has one.
    pub fn cycle_start(next: &[Option<usize>], head: Option<usize>) -> Option<usize> {
        let (mut slow, mut fast) = (head, head);
        loop {
            slow = step(next, slow);
            fast = step(next, step(next, fast));
            match (slow, fast) {
                (Some(s), Some(f)) if s == f => break,
                (_, None) => return None,
                _ => {}
            }
        }
        // Floyd: from the meeting point and from the head, the cycle start is equally far.
        let (mut a, mut b) = (head, slow);
        while a != b {
            a = step(next, a);
            b = step(next, b);
        }
        a
    }

    pub fn has_cycle(next: &[Option<usize>], head: Option<usize>) -> bool {
        cycle_start(next, head).is_some()
    }
    """,
    [T("cycle", "0→1→2→3→1", "cycle_start(&[Some(1), Some(2), Some(3), Some(1)], Some(0))", "Some(1)"),
     T("no_cycle", "0→1→end", "(cycle_start(&[Some(1), None], Some(0)), has_cycle(&[Some(1), None], Some(0)))", "(None, false)"),
     T("two_node_cycle", "0→1→0", "(cycle_start(&[Some(1), Some(0)], Some(0)), has_cycle(&[Some(1), Some(0)], Some(0)))", "(Some(0), true)"),
     T("single_no_cycle", "0→end", "cycle_start(&[None], Some(0))", "None"),
     T("empty", "no head", "cycle_start(&[], None)", "None")],
    [T("self_loop", "0→0", "cycle_start(&[Some(0)], Some(0))", "Some(0)"),
     T("empty", "no head", "cycle_start(&[], None)", "None"),
     T("head_not_zero", "3→1→2→1, node 0 unused", "cycle_start(&[None, Some(2), Some(1), Some(1)], Some(3))", "Some(1)"),
     T("tail_self_loop", "0→1→2→2", "cycle_start(&[Some(1), Some(2), Some(2)], Some(0))", "Some(2)"),
     T("cycle_elsewhere", "head 0→1→end; 2→3→2 is not reachable", "cycle_start(&[Some(1), None, Some(3), Some(2)], Some(0))", "None"),
     T("whole_list_is_cycle", "0→1→2→3→4→0", "cycle_start(&[Some(1), Some(2), Some(3), Some(4), Some(0)], Some(0))", "Some(0)"),
     T("long_tail_short_cycle", "0→1→…→999→998", "cycle_start(&next, Some(0))", "Some(998)",
       setup="let mut next: Vec<Option<usize>> = (1..=1000).map(Some).collect();\nnext[999] = Some(998);"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(510);
         for _ in 0..300 {
             let n = 1 + rng.below(10);
             let next: Vec<Option<usize>> = (0..n).map(|_| if rng.below(4) == 0 { None } else { Some(rng.below(n)) }).collect();
             let head = if rng.below(10) == 0 { None } else { Some(rng.below(n)) };
             // Reference: walk and remember when each node was first seen.
             let mut seen = vec![false; n];
             let mut cur = head;
             let mut want = None;
             while let Some(i) = cur {
                 if seen[i] {
                     want = Some(i);
                     break;
                 }
                 seen[i] = true;
                 cur = next[i];
             }
             check!(format!("next = {next:?}, head = {head:?}"), (cycle_start(&next, head), has_cycle(&next, head)), (want, want.is_some()));
         }
     }

     #[test]
     fn scale_200k() {
         let mut next: Vec<Option<usize>> = (1..=200_000).map(Some).collect();
         next[199_999] = Some(123_456);
         let mut straight = next.clone();
         straight[199_999] = None;
         check!("200000 nodes, last → 123456; and the same without the back link", (cycle_start(&next, Some(0)), cycle_start(&straight, Some(0))), (Some(123_456), None));
     }
     """,
     T("big_loop", "10⁵ nodes, last points to 40_000", "cycle_start(&next, Some(0))", "Some(40_000)",
       setup="let mut next: Vec<Option<usize>> = (1..=100_000).map(Some).collect();\nnext[99_999] = Some(40_000);")],
    [("approach", "Floyd: a slow and a fast pointer meet inside the cycle. Then one pointer from the head and one from the meeting point meet at the cycle's start."),
     ("rust", "Indices are `Copy` and can point anywhere, including backwards: that's how Rust code represents cyclic structure without `Rc` cycles.")],
    ("Floyd's algorithm needs only two indices. Storing `next` as `Vec<Option<usize>>` is the arena pattern used for graphs and lists that aren't trees.", "O(n)", "O(1)"),
    "How would you get a cycle with `Rc<RefCell<Node>>`, and what happens to its memory?",
    ["Arenas of indices for cyclic structures.", "Floyd's cycle detection."],
    related=["D9", "S7"],
    constraints=["0 ≤ next.len() ≤ 2·10⁵"],
    wrong=dict(
        returns_the_meeting_point="""
            fn step(next: &[Option<usize>], i: Option<usize>) -> Option<usize> {
                i.and_then(|i| next[i])
            }

            /// Where the list starting at `head` enters a cycle, if it has one.
            pub fn cycle_start(next: &[Option<usize>], head: Option<usize>) -> Option<usize> {
                let (mut slow, mut fast) = (head, head);
                loop {
                    slow = step(next, slow);
                    fast = step(next, step(next, fast));
                    match (slow, fast) {
                        (Some(s), Some(f)) if s == f => return Some(s),
                        (_, None) => return None,
                        _ => {}
                    }
                }
            }

            pub fn has_cycle(next: &[Option<usize>], head: Option<usize>) -> bool {
                cycle_start(next, head).is_some()
            }
        """,
        remembers_the_path_in_a_vec="""
            /// Where the list starting at `head` enters a cycle, if it has one.
            pub fn cycle_start(next: &[Option<usize>], head: Option<usize>) -> Option<usize> {
                let mut path: Vec<usize> = Vec::new();
                let mut cur = head;
                while let Some(i) = cur {
                    if path.contains(&i) {
                        return Some(i);
                    }
                    path.push(i);
                    cur = next[i];
                }
                None
            }

            pub fn has_cycle(next: &[Option<usize>], head: Option<usize>) -> bool {
                cycle_start(next, head).is_some()
            }
        """,
        bounded_walk="""
            /// Where the list starting at `head` enters a cycle, if it has one.
            pub fn cycle_start(next: &[Option<usize>], head: Option<usize>) -> Option<usize> {
                // A path longer than the arena must repeat; guess that the head is where it loops.
                let mut cur = head;
                for _ in 0..next.len() {
                    cur = cur.and_then(|i| next[i]);
                }
                cur.and(head)
            }

            pub fn has_cycle(next: &[Option<usize>], head: Option<usize>) -> bool {
                cycle_start(next, head).is_some()
            }
        """,
    ),
))

RNODE = """
use std::cell::RefCell;
use std::collections::HashMap;
use std::rc::{Rc, Weak};

pub struct RNode {
    pub val: i32,
    pub next: Option<Rc<RefCell<RNode>>>,
    /// Weak, so `random` can point backwards without a reference cycle.
    pub random: Option<Weak<RefCell<RNode>>>,
}

pub type RLink = Option<Rc<RefCell<RNode>>>;

/// Builds a list from `(value, random index)` pairs.
pub fn build(spec: &[(i32, Option<usize>)]) -> RLink {
    let nodes: Vec<Rc<RefCell<RNode>>> = spec
        .iter()
        .map(|&(val, _)| Rc::new(RefCell::new(RNode { val, next: None, random: None })))
        .collect();
    for (i, &(_, r)) in spec.iter().enumerate() {
        let mut n = nodes[i].borrow_mut();
        n.next = nodes.get(i + 1).cloned();
        n.random = r.map(|r| Rc::downgrade(&nodes[r]));
    }
    nodes.first().cloned()
}
"""

P.append(prob(
    "copy-list-with-random-pointer", "Copy list with random pointer (into an arena)", "medium", "cursors", ["Rc::as_ptr", "Weak", "arena"],
    """
    Each node has `next` and a `random` pointer to any node (or none). Copy the list into an arena:
    `Vec<(value, random index)>` in list order, where the random index is the position of the node it points to.
    """,
    RNODE.strip("\n") + """

pub fn to_arena(head: &RLink) -> Vec<(i32, Option<usize>)> {
    todo!()
}
""",
    RNODE.strip("\n") + """

pub fn to_arena(head: &RLink) -> Vec<(i32, Option<usize>)> {
    let mut order: Vec<Rc<RefCell<RNode>>> = Vec::new();
    let mut cur = head.clone();
    while let Some(node) = cur {
        cur = node.borrow().next.clone();
        order.push(node);
    }
    // A node's identity is its address.
    let index: HashMap<*const RefCell<RNode>, usize> = order.iter().enumerate().map(|(i, n)| (Rc::as_ptr(n), i)).collect();
    order
        .iter()
        .map(|n| {
            let n = n.borrow();
            let random = n.random.as_ref().and_then(Weak::upgrade).map(|r| index[&Rc::as_ptr(&r)]);
            (n.val, random)
        })
        .collect()
}
""",
    [T("example", "[(7,-),(13,0),(11,4),(10,2),(1,0)]", "to_arena(&build(&spec))", "spec.to_vec()",
       setup="let spec = [(7, None), (13, Some(0)), (11, Some(4)), (10, Some(2)), (1, Some(0))];"),
     T("empty", "[]", "to_arena(&None)", "vec![]"),
     T("both_point_to_second", "[(1,1),(2,1)]", "to_arena(&build(&spec))", "spec.to_vec()", setup="let spec = [(1, Some(1)), (2, Some(1))];"),
     T("equal_values", "[(3,-),(3,0),(3,-)]", "to_arena(&build(&spec))", "spec.to_vec()", setup="let spec = [(3, None), (3, Some(0)), (3, None)];"),
     T("single_no_random", "[(9,-)]", "to_arena(&build(&spec))", "spec.to_vec()", setup="let spec = [(9, None)];")],
    [T("self_random", "[(1,0),(2,1)]", "to_arena(&build(&spec))", "spec.to_vec()", setup="let spec = [(1, Some(0)), (2, Some(1))];"),
     T("single_self", "[(4,0)]", "to_arena(&build(&spec))", "spec.to_vec()", setup="let spec = [(4, Some(0))];"),
     T("all_to_last", "four nodes, every random → 3", "to_arena(&build(&spec))", "spec.to_vec()", setup="let spec = [(1, Some(3)), (2, Some(3)), (3, Some(3)), (4, Some(3))];"),
     T("extremes", "[(MIN,1),(MAX,0)]", "to_arena(&build(&spec))", "spec.to_vec()", setup="let spec = [(i32::MIN, Some(1)), (i32::MAX, Some(0))];"),
     T("list_unchanged", "the list reads the same afterwards", "(to_arena(&head), to_arena(&head))", "(spec.to_vec(), spec.to_vec())",
       setup="let spec = [(1, Some(2)), (2, None), (3, Some(0))];\nlet head = build(&spec);"),
     """
     /// Unlinks a long Rc list one node at a time (the default drop recurses once per node).
     fn free(mut cur: RLink) {
         while let Some(node) = cur {
             cur = node.borrow_mut().next.take();
         }
     }

     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(511);
         for _ in 0..300 {
             let n = rng.below(8);
             let spec: Vec<(i32, Option<usize>)> = (0..n).map(|_| (rng.int(0, 2) as i32, if rng.bool() { Some(rng.below(n)) } else { None })).collect();
             check!(format!("{spec:?}"), to_arena(&build(&spec)), spec.clone());
         }
     }

     #[test]
     fn scale_100k() {
         let n = 100_000;
         let spec: Vec<(i32, Option<usize>)> = (0..n).map(|i| (7, Some((i * 7_919 + 13) % n))).collect();
         let head = build(&spec);
         let got = to_arena(&head);
         free(head);
         check!("100000 nodes, all value 7, random = (7919 i + 13) % n", got == spec, true);
     }
     """,
     T("equal_values", "three nodes with value 5", "to_arena(&build(&spec))", "spec.to_vec()", setup="let spec = [(5, Some(2)), (5, None), (5, Some(0))];"),
     T("long", "2000 nodes, random = reversed index", "to_arena(&build(&spec)) == spec", "true",
       setup="let spec: Vec<(i32, Option<usize>)> = (0..2_000).map(|i| (i as i32, Some(1_999 - i))).collect();")],
    [("approach", "Two passes: number the nodes in order, then look up where each `random` points."),
     ("rust", "Values can repeat, so identify nodes by address: `Rc::as_ptr(&rc)` as a `HashMap` key."),
     ("rust", "`random` is a `Weak`: `upgrade()` gives an `Rc` while the node is alive.")],
    ("The arena form is how Rust code usually stores pointer-y structures: indices instead of references, so copying is just copying a `Vec`.", "O(n)", "O(n)"),
    "Convert the arena back into `RNode`s. Why is that direction easier?",
    ["`Rc::as_ptr` for node identity.", "`Weak` for non-owning back pointers."],
    related=["S7", "D9"],
    constraints=["0 ≤ list length ≤ 10⁵"],
    wrong=dict(
        matches_by_value=RNODE.strip("\n") + """

pub fn to_arena(head: &RLink) -> Vec<(i32, Option<usize>)> {
    let mut order: Vec<Rc<RefCell<RNode>>> = Vec::new();
    let mut cur = head.clone();
    while let Some(node) = cur {
        cur = node.borrow().next.clone();
        order.push(node);
    }
    // The first node with the target's value.
    let index: HashMap<i32, usize> = order.iter().enumerate().rev().map(|(i, n)| (n.borrow().val, i)).collect();
    order
        .iter()
        .map(|n| {
            let n = n.borrow();
            let random = n.random.as_ref().and_then(Weak::upgrade).map(|r| index[&r.borrow().val]);
            (n.val, random)
        })
        .collect()
}
""",
        walks_from_the_head_for_each_random=RNODE.strip("\n") + """

pub fn to_arena(head: &RLink) -> Vec<(i32, Option<usize>)> {
    let mut out = Vec::new();
    let mut cur = head.clone();
    while let Some(node) = cur {
        let random = node.borrow().random.as_ref().and_then(Weak::upgrade).map(|target| {
            // Count steps from the head until we reach the target node.
            let mut i = 0;
            let mut walk = head.clone();
            while let Some(w) = walk {
                if Rc::ptr_eq(&w, &target) {
                    break;
                }
                walk = w.borrow().next.clone();
                i += 1;
            }
            i
        });
        out.push((node.borrow().val, random));
        cur = node.borrow().next.clone();
    }
    out
}
""",
    ),
))

# ---------------------------------------------------------------- beyond Box (hard)

P.append(prob(
    "merge-k-sorted-lists", "Merge k sorted lists", "hard", "beyond-box", ["BinaryHeap", "Reverse", "Blind 75"],
    "Merge `k` sorted lists into one sorted list by relinking nodes.",
    with_list("""
use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn merge_k(lists: Vec<Option<Box<ListNode>>>) -> Option<Box<ListNode>> {
    todo!()
}
"""),
    with_list("""
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
"""),
    [T("three", "[[1,4,5],[1,3,4],[2,6]]", "values(&merge_k(vec![list(&[1, 4, 5]), list(&[1, 3, 4]), list(&[2, 6])]))", "vec![1, 1, 2, 3, 4, 4, 5, 6]"),
     T("none", "[]", "merge_k(vec![])", "None"),
     T("one_empty_list", "[[]]", "merge_k(vec![None])", "None"),
     T("single_list", "[[1,2,3]]", "values(&merge_k(vec![list(&[1, 2, 3])]))", "vec![1, 2, 3]"),
     T("some_empty", "[[],[2],[],[1,3]]", "values(&merge_k(vec![None, list(&[2]), None, list(&[1, 3])]))", "vec![1, 2, 3]")],
    [T("empty_lists", "[[],[]]", "merge_k(vec![None, None])", "None"),
     T("duplicates_across", "[[1,1],[1],[1,1,1]]", "values(&merge_k(vec![list(&[1, 1]), list(&[1]), list(&[1, 1, 1])]))", "vec![1; 6]"),
     T("extremes", "[[MIN,MAX],[0]]", "values(&merge_k(vec![list(&[i32::MIN, i32::MAX]), list(&[0])]))", "vec![i32::MIN, 0, i32::MAX]"),
     T("uneven_lengths", "[[5],[1,2,3,4,6,7]]", "values(&merge_k(vec![list(&[5]), list(&[1, 2, 3, 4, 6, 7])]))", "vec![1, 2, 3, 4, 5, 6, 7]"),
     T("two_lists", "[[2,4],[1,3]]", "values(&merge_k(vec![list(&[2, 4]), list(&[1, 3])]))", "vec![1, 2, 3, 4]"),
     FREE,
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(512);
         for _ in 0..300 {
             let k = rng.below(5);
             let lists: Vec<Vec<i32>> = (0..k).map(|_| { let n = rng.below(5); let mut v: Vec<i32> = rng.vec(n, -9, 9); v.sort(); v }).collect();
             let mut want: Vec<i32> = lists.concat();
             want.sort();
             check!(format!("{lists:?}"), values(&merge_k(lists.iter().map(|v| list(v)).collect())), want);
         }
     }

     #[test]
     fn scale_50k_lists() {
         // 50000 lists of 4 values each: list j holds j, j + 50000, j + 100000, j + 150000.
         let k = 50_000;
         let lists: Vec<_> = (0..k).map(|j| list(&[j, j + k, j + 2 * k, j + 3 * k])).collect();
         let m = merge_k(lists);
         let got = values(&m);
         free(m);
         check!("50000 lists of 4 values", got == (0..4 * k).collect::<Vec<_>>(), true);
     }
     """,
     T("negatives", "[[-3,0],[-5]]", "values(&merge_k(vec![list(&[-3, 0]), list(&[-5])]))", "vec![-5, -3, 0]"),
     T("many", "100 lists × 100 values", "values(&merge_k(lists)) == (0..10_000).collect::<Vec<_>>()", "true",
       setup="let lists: Vec<_> = (0..100).map(|k| list(&(0..100).map(|i| i * 100 + k).collect::<Vec<i32>>())).collect();")],
    [("approach", "Keep the front of every list in a min-heap; repeatedly take the smallest and push that list's next front."),
     ("rust", "Put `(value, list index)` in the heap, not the boxed node: the nodes stay in `lists`, which avoids ordering `Box<ListNode>`."),
     ("rust", "`BinaryHeap` is a max-heap; wrap entries in `Reverse` for smallest-first.")],
    ("The heap stores small `Copy` keys and the lists keep ownership of the nodes, so there's no need to implement `Ord` for `ListNode`.", "O(N log k)", "O(k)"),
    "Solve it by merging pairs of lists (divide and conquer). Compare the costs.",
    ["Heap of keys + indices, with ownership kept elsewhere.", "`Reverse` for a min-heap."],
    related=["D7", "S5"],
    constraints=["0 ≤ k ≤ 5·10⁴", "0 ≤ total length ≤ 2·10⁵"],
    wrong=dict(
        scan_every_front=with_list("""
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
"""),
        max_heap=with_list("""
use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn merge_k(mut lists: Vec<Option<Box<ListNode>>>) -> Option<Box<ListNode>> {
    let mut heap: BinaryHeap<(i32, usize)> = lists.iter().enumerate().filter_map(|(i, l)| l.as_ref().map(|n| (n.val, i))).collect();
    let mut head = None;
    let mut tail = &mut head;
    while let Some((_, i)) = heap.pop() {
        let mut node = lists[i].take().expect("the heap only names non-empty lists");
        lists[i] = node.next.take();
        if let Some(n) = &lists[i] {
            heap.push((n.val, i));
        }
        tail = &mut tail.insert(node).next;
    }
    head
}
"""),
        only_the_first_node_of_each=with_list("""
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
"""),
    ),
))

P.append(prob(
    "reverse-nodes-in-k-group", "Reverse nodes in k-group", "hard", "beyond-box", ["&mut cursor", "take"],
    """
    Reverse every consecutive group of `k` nodes; a final group shorter than `k` stays as it is. Relink nodes;
    don't copy values. `k = 0` or `1` leaves the list unchanged.
    """,
    with_list("""
pub fn reverse_k_group(head: Option<Box<ListNode>>, k: usize) -> Option<Box<ListNode>> {
    todo!()
}
"""),
    with_list("""
pub fn reverse_k_group(mut head: Option<Box<ListNode>>, k: usize) -> Option<Box<ListNode>> {
    if k < 2 {
        return head;
    }
    // `slot` is where the next group starts: `head`, then the `next` of each reversed group's last node.
    let mut slot = &mut head;
    loop {
        let mut probe = slot.as_deref();
        let mut have = 0;
        while have < k {
            let Some(node) = probe else { break };
            probe = node.next.as_deref();
            have += 1;
        }
        if have < k {
            break;
        }
        // Detach k nodes, reversing them as they come off.
        let mut rest = slot.take();
        let mut group = None;
        for _ in 0..k {
            let mut node = rest.expect("counted k nodes");
            rest = node.next.take();
            node.next = group;
            group = Some(node);
        }
        *slot = group;
        for _ in 0..k {
            slot = &mut slot.as_mut().expect("k nodes in the group").next;
        }
        *slot = rest;
    }
    head
}
"""),
    [T("k2", "[1,2,3,4,5], k = 2", "values(&reverse_k_group(list(&[1, 2, 3, 4, 5]), 2))", "vec![2, 1, 4, 3, 5]"),
     T("k3", "[1,2,3,4,5], k = 3", "values(&reverse_k_group(list(&[1, 2, 3, 4, 5]), 3))", "vec![3, 2, 1, 4, 5]"),
     T("k1", "[1,2,3], k = 1", "values(&reverse_k_group(list(&[1, 2, 3]), 1))", "vec![1, 2, 3]"),
     T("too_long", "[1,2], k = 3", "values(&reverse_k_group(list(&[1, 2]), 3))", "vec![1, 2]"),
     T("empty", "[], k = 2", "reverse_k_group(None, 2)", "None")],
    [T("k1", "[1,2,3], k = 1", "values(&reverse_k_group(list(&[1, 2, 3]), 1))", "vec![1, 2, 3]"),
     T("k0", "[1,2,3], k = 0", "values(&reverse_k_group(list(&[1, 2, 3]), 0))", "vec![1, 2, 3]"),
     T("empty", "[], k = 2", "reverse_k_group(None, 2)", "None"),
     T("exact_multiple", "[1..=6], k = 2", "values(&reverse_k_group(list(&[1, 2, 3, 4, 5, 6]), 2))", "vec![2, 1, 4, 3, 6, 5]"),
     T("short_tail_kept", "[1..=8], k = 3", "values(&reverse_k_group(list(&[1, 2, 3, 4, 5, 6, 7, 8]), 3))", "vec![3, 2, 1, 6, 5, 4, 7, 8]"),
     T("k_len_minus_one", "[1,2,3,4], k = 3", "values(&reverse_k_group(list(&[1, 2, 3, 4]), 3))", "vec![3, 2, 1, 4]"),
     FREE,
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(513);
         for _ in 0..300 {
             let n = rng.below(12);
             let v: Vec<i32> = (0..n as i32).collect();
             let k = rng.below(6);
             let mut want = v.clone();
             if k >= 2 {
                 for chunk in want.chunks_exact_mut(k) {
                     chunk.reverse();
                 }
             }
             check!(format!("{v:?}, k = {k}"), values(&reverse_k_group(list(&v), k)), want);
         }
     }

     #[test]
     fn scale_200k_pairs() {
         let l = reverse_k_group(list(&(0..200_000).collect::<Vec<i32>>()), 2);
         let got = values(&l);
         free(l);
         check!("0..200000, k = 2", (got.len(), got[0], got[1], got[199_998], got[199_999]), (200_000, 1, 0, 199_999, 199_998));
     }
     """,
     T("whole", "[1,2,3], k = 3", "values(&reverse_k_group(list(&[1, 2, 3]), 3))", "vec![3, 2, 1]"),
     T("too_long", "[1,2], k = 3", "values(&reverse_k_group(list(&[1, 2]), 3))", "vec![1, 2]"),
     T("long", "10⁴ nodes, k = 100", "{ let v = values(&reverse_k_group(list(&(0..10_000).collect::<Vec<i32>>()), 100)); (v[0], v[99], v[100], v.len()) }", "(99, 0, 199, 10_000)")],
    [("approach", "For each group: check k nodes remain, detach them while reversing, reattach, then move the slot cursor to the group's new last node."),
     ("rust", "Look ahead with a shared `as_deref()` probe first; the `&mut` slot is only used after that borrow ends."),
     ("rust", "Walking the slot k steps after reattaching costs O(k) per group, O(n) overall, and avoids holding a pointer to the group's tail.")],
    ("Keeping one mutable cursor (`slot`) and one owned remainder (`rest`) at a time is what makes this pass the borrow checker without `unsafe` or `Rc`.", "O(n)", "O(1)"),
    "Could you avoid the second walk to the group's tail? What would you need to hold onto?",
    ["Lookahead with shared borrows, then mutation.", "A single `&mut` slot cursor."],
    constraints=["0 ≤ list length ≤ 2·10⁵"],
    wrong=dict(
        reverses_the_short_tail=with_list("""
pub fn reverse_k_group(mut head: Option<Box<ListNode>>, k: usize) -> Option<Box<ListNode>> {
    if k < 2 {
        return head;
    }
    let mut slot = &mut head;
    while slot.is_some() {
        let mut rest = slot.take();
        let mut group = None;
        let mut taken = 0;
        while taken < k {
            let Some(mut node) = rest else { break };
            rest = node.next.take();
            node.next = group;
            group = Some(node);
            taken += 1;
        }
        *slot = group;
        for _ in 0..taken {
            slot = &mut slot.as_mut().expect("in the group").next;
        }
        *slot = rest;
    }
    head
}
"""),
        recursive=with_list("""
pub fn reverse_k_group(head: Option<Box<ListNode>>, k: usize) -> Option<Box<ListNode>> {
    if k < 2 {
        return head;
    }
    let mut probe = head.as_deref();
    for _ in 0..k {
        match probe {
            Some(n) => probe = n.next.as_deref(),
            None => return head,
        }
    }
    let mut rest = head;
    let mut group = None;
    for _ in 0..k {
        let mut node = rest.expect("counted k nodes");
        rest = node.next.take();
        node.next = group;
        group = Some(node);
    }
    // The old first node is now the group's last: attach the rest, reversed the same way.
    let mut last = &mut group;
    while last.as_ref().is_some_and(|n| n.next.is_some()) {
        last = &mut last.as_mut().expect("checked").next;
    }
    last.as_mut().expect("k nodes").next = reverse_k_group(rest, k);
    group
}
"""),
        rescans_from_the_head=with_list("""
pub fn reverse_k_group(mut head: Option<Box<ListNode>>, k: usize) -> Option<Box<ListNode>> {
    if k < 2 {
        return head;
    }
    let mut done = 0;
    loop {
        // Walk from the head to the start of the next group every time.
        let mut slot = &mut head;
        for _ in 0..done {
            slot = &mut slot.as_mut().expect("already reversed").next;
        }
        let mut probe = slot.as_deref();
        let mut have = 0;
        while have < k {
            let Some(node) = probe else { break };
            probe = node.next.as_deref();
            have += 1;
        }
        if have < k {
            break;
        }
        let mut rest = slot.take();
        let mut group = None;
        for _ in 0..k {
            let mut node = rest.expect("counted k nodes");
            rest = node.next.take();
            node.next = group;
            group = Some(node);
        }
        *slot = group;
        for _ in 0..k {
            slot = &mut slot.as_mut().expect("k nodes in the group").next;
        }
        *slot = rest;
        done += k;
    }
    head
}
"""),
    ),
))

DEQUE_STARTER = """
use std::cell::RefCell;
use std::rc::{Rc, Weak};

struct Node {
    val: i32,
    next: Option<Rc<RefCell<Node>>>,
    /// Weak: the next node owns this one's successor, not the other way round.
    prev: Weak<RefCell<Node>>,
}

#[derive(Default)]
pub struct Deque {
    head: Option<Rc<RefCell<Node>>>,
    tail: Option<Rc<RefCell<Node>>>,
    len: usize,
}
"""

DEQUE_SOLUTION = DEQUE_STARTER.strip("\n") + """

impl Deque {
    pub fn new() -> Self {
        Self::default()
    }

    fn node(val: i32) -> Rc<RefCell<Node>> {
        Rc::new(RefCell::new(Node { val, next: None, prev: Weak::new() }))
    }

    pub fn push_front(&mut self, val: i32) {
        let node = Self::node(val);
        match self.head.take() {
            Some(old) => {
                old.borrow_mut().prev = Rc::downgrade(&node);
                node.borrow_mut().next = Some(old);
            }
            None => self.tail = Some(Rc::clone(&node)),
        }
        self.head = Some(node);
        self.len += 1;
    }

    pub fn push_back(&mut self, val: i32) {
        let node = Self::node(val);
        match self.tail.take() {
            Some(old) => {
                node.borrow_mut().prev = Rc::downgrade(&old);
                old.borrow_mut().next = Some(Rc::clone(&node));
            }
            None => self.head = Some(Rc::clone(&node)),
        }
        self.tail = Some(node);
        self.len += 1;
    }

    /// Unwraps a node that nothing else points to any more.
    fn into_val(node: Rc<RefCell<Node>>) -> i32 {
        match Rc::try_unwrap(node) {
            Ok(cell) => cell.into_inner().val,
            Err(_) => unreachable!("a popped node has no other owners"),
        }
    }

    pub fn pop_front(&mut self) -> Option<i32> {
        let old = self.head.take()?;
        match old.borrow_mut().next.take() {
            Some(next) => {
                next.borrow_mut().prev = Weak::new();
                self.head = Some(next);
            }
            None => self.tail = None,
        }
        self.len -= 1;
        Some(Self::into_val(old))
    }

    pub fn pop_back(&mut self) -> Option<i32> {
        let old = self.tail.take()?;
        let prev = old.borrow().prev.upgrade();
        match prev {
            Some(prev) => {
                prev.borrow_mut().next = None;
                self.tail = Some(prev);
            }
            None => self.head = None,
        }
        self.len -= 1;
        Some(Self::into_val(old))
    }

    pub fn front(&self) -> Option<i32> {
        self.head.as_ref().map(|n| n.borrow().val)
    }

    pub fn back(&self) -> Option<i32> {
        self.tail.as_ref().map(|n| n.borrow().val)
    }

    pub fn len(&self) -> usize {
        self.len
    }

    pub fn is_empty(&self) -> bool {
        self.len == 0
    }
}

impl Drop for Deque {
    // Unlink one node at a time; the default drop would recurse down the `next` chain.
    fn drop(&mut self) {
        while self.pop_front().is_some() {}
    }
}
"""

DEQUE_DROP = DEQUE_SOLUTION[DEQUE_SOLUTION.index("impl Drop for Deque {"):]

P.append(prob(
    "doubly-linked-deque-rc-weak", "Doubly linked deque with Rc and Weak", "hard", "beyond-box", ["Rc<RefCell>", "Weak", "try_unwrap"],
    """
    Implement a deque as a doubly linked list: `next` links are `Rc`, `prev` links are `Weak`, so nodes don't
    keep each other alive. Popping must give back the value without cloning the node.
    """,
    DEQUE_STARTER.strip("\n") + """

impl Deque {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn push_front(&mut self, val: i32) {
        todo!()
    }

    pub fn push_back(&mut self, val: i32) {
        todo!()
    }

    pub fn pop_front(&mut self) -> Option<i32> {
        todo!()
    }

    pub fn pop_back(&mut self) -> Option<i32> {
        todo!()
    }

    pub fn front(&self) -> Option<i32> {
        todo!()
    }

    pub fn back(&self) -> Option<i32> {
        todo!()
    }

    pub fn len(&self) -> usize {
        self.len
    }

    pub fn is_empty(&self) -> bool {
        self.len == 0
    }
}
""",
    DEQUE_SOLUTION,
    [T("both_ends", "push_back 1,2; push_front 0; pop_back, pop_front", "(d.pop_back(), d.pop_front(), d.front(), d.back(), d.len())", "(Some(2), Some(0), Some(1), Some(1), 1)",
       setup="let mut d = Deque::new();\nd.push_back(1);\nd.push_back(2);\nd.push_front(0);"),
     T("empty", "new deque", "(d.pop_front(), d.pop_back(), d.front(), d.is_empty())", "(None, None, None, true)", setup="let mut d = Deque::new();"),
     T("single_both_ways", "push 7; pop_back; then push 8; pop_front", "{ d.push_back(7); let a = d.pop_back(); d.push_front(8); (a, d.pop_front(), d.is_empty()) }", "(Some(7), Some(8), true)",
       setup="let mut d = Deque::new();"),
     T("fifo", "push_back 1,2,3; pop_front three times", "(d.pop_front(), d.pop_front(), d.pop_front(), d.len())", "(Some(1), Some(2), Some(3), 0)",
       setup="let mut d = Deque::new();\nd.push_back(1);\nd.push_back(2);\nd.push_back(3);"),
     T("front_and_back_peek", "push_front 2, push_front 1, push_back 3", "(d.front(), d.back(), d.len())", "(Some(1), Some(3), 3)",
       setup="let mut d = Deque::new();\nd.push_front(2);\nd.push_front(1);\nd.push_back(3);")],
    [T("single_both_ways", "push 7; pop_back; then push 8; pop_front", "{ d.push_back(7); let a = d.pop_back(); d.push_front(8); (a, d.pop_front(), d.is_empty()) }", "(Some(7), Some(8), true)",
       setup="let mut d = Deque::new();"),
     T("reuse_after_empty", "push_front 1; pop_front; push_back 2, 3; pop_back", "{ d.push_front(1); d.pop_front(); d.push_back(2); d.push_back(3); (d.pop_back(), d.front(), d.back(), d.len()) }", "(Some(3), Some(2), Some(2), 1)",
       setup="let mut d = Deque::new();"),
     T("pop_front_to_empty_then_back", "push_back 1,2; pop_front twice; pop_back", "(d.pop_front(), d.pop_front(), d.pop_back(), d.back())", "(Some(1), Some(2), None, None)",
       setup="let mut d = Deque::new();\nd.push_back(1);\nd.push_back(2);"),
     T("extremes", "push i32::MIN front, i32::MAX back", "(d.pop_back(), d.pop_back())", "(Some(i32::MAX), Some(i32::MIN))",
       setup="let mut d = Deque::new();\nd.push_front(i32::MIN);\nd.push_back(i32::MAX);"),
     T("drain_from_front_pushed_front", "push_front 0..5; pop_front until empty", "out", "vec![4, 3, 2, 1, 0]",
       setup="let mut d = Deque::new();\nfor i in 0..5 {\n    d.push_front(i);\n}\nlet out: Vec<i32> = std::iter::from_fn(|| d.pop_front()).collect();"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(514);
         for _ in 0..300 {
             let mut d = Deque::new();
             let mut model = std::collections::VecDeque::new();
             let mut ops: Vec<String> = Vec::new();
             for _ in 0..12 {
                 let x = rng.int(-9, 9) as i32;
                 match rng.below(4) {
                     0 => {
                         d.push_front(x);
                         model.push_front(x);
                         ops.push(format!("push_front {x}"));
                     }
                     1 => {
                         d.push_back(x);
                         model.push_back(x);
                         ops.push(format!("push_back {x}"));
                     }
                     2 => {
                         ops.push("pop_front".into());
                         check!(format!("{ops:?}"), d.pop_front(), model.pop_front());
                     }
                     _ => {
                         ops.push("pop_back".into());
                         check!(format!("{ops:?}"), d.pop_back(), model.pop_back());
                     }
                 }
                 check!(format!("{ops:?}: front, back, len"), (d.front(), d.back(), d.len(), d.is_empty()), (model.front().copied(), model.back().copied(), model.len(), model.is_empty()));
             }
         }
     }
     """,
     T("drain_from_back", "push_back 0..5; pop_back until empty", "out", "vec![4, 3, 2, 1, 0]",
       setup="let mut d = Deque::new();\nfor i in 0..5 {\n    d.push_back(i);\n}\nlet out: Vec<i32> = std::iter::from_fn(|| d.pop_back()).collect();"),
     T("big_drop", "push 10⁶ then drop", "d.len()", "1_000_000", setup="let mut d = Deque::new();\nfor i in 0..1_000_000 {\n    d.push_back(i);\n}")],
    [("rust", "`next: Rc`, `prev: Weak`: ownership runs one way, so dropping the head frees the chain and there's no reference cycle."),
     ("rust", "When a node is popped, clear every other strong reference first (`head`/`tail`/the neighbour's `next`), then `Rc::try_unwrap` it to get the value out."),
     ("edge case", "A one-element deque has `head` and `tail` pointing at the same node; both must be cleared.")],
    ("Every operation is O(1), but it costs a refcount, a RefCell flag and a heap allocation per node. `impl Drop` pops iteratively; the default drop would recurse through a million `next` links and overflow the stack.", "O(1) per op", "O(n)"),
    "Add `iter()` returning `impl Iterator<Item = i32>`. Why can't it return `&i32`s?",
    ["`Rc` forward, `Weak` backward.", "`Rc::try_unwrap` to recover a value.", "Iterative `Drop` for long chains."],
    related=["S7", "L7"],
    wrong=dict(
        default_drop=DEQUE_SOLUTION.replace(DEQUE_DROP, ""),
        pop_front_keeps_the_tail=DEQUE_SOLUTION.replace("""            None => self.tail = None,
        }
        self.len -= 1;
        Some(Self::into_val(old))
    }

    pub fn pop_back""", """            None => {}
        }
        self.len -= 1;
        Some(Self::into_val(old))
    }

    pub fn pop_back""").replace("""            Err(_) => unreachable!("a popped node has no other owners"),""", """            Err(rc) => rc.borrow().val,"""),
        pop_back_forgets_len=DEQUE_SOLUTION.replace("""            None => self.head = None,
        }
        self.len -= 1;""", """            None => self.head = None,
        }"""),
    ),
))

NN_STARTER = """
use std::marker::PhantomData;
use std::ptr::NonNull;

struct Node {
    val: i32,
    prev: Option<NonNull<Node>>,
    next: Option<NonNull<Node>>,
}

/// A doubly linked list that owns its nodes through raw pointers.
pub struct LinkedList {
    head: Option<NonNull<Node>>,
    tail: Option<NonNull<Node>>,
    len: usize,
    /// Tells the compiler (and drop check) that we own `Box<Node>`s.
    _owns: PhantomData<Box<Node>>,
}

pub struct Iter<'a> {
    next: Option<NonNull<Node>>,
    _list: PhantomData<&'a Node>,
}
"""

NN_SOLUTION = NN_STARTER.strip("\n") + """

impl Default for LinkedList {
    fn default() -> Self {
        LinkedList { head: None, tail: None, len: 0, _owns: PhantomData }
    }
}

impl LinkedList {
    pub fn new() -> Self {
        Self::default()
    }

    fn alloc(val: i32, prev: Option<NonNull<Node>>, next: Option<NonNull<Node>>) -> NonNull<Node> {
        NonNull::from(Box::leak(Box::new(Node { val, prev, next })))
    }

    pub fn push_front(&mut self, val: i32) {
        let node = Self::alloc(val, None, self.head);
        match self.head {
            // SAFETY: `h` came from `alloc` and is owned by this list until popped; `&mut self` means no other access.
            Some(mut h) => unsafe { h.as_mut().prev = Some(node) },
            None => self.tail = Some(node),
        }
        self.head = Some(node);
        self.len += 1;
    }

    pub fn push_back(&mut self, val: i32) {
        let node = Self::alloc(val, self.tail, None);
        match self.tail {
            // SAFETY: as in push_front: a live node we own, accessed through `&mut self`.
            Some(mut t) => unsafe { t.as_mut().next = Some(node) },
            None => self.head = Some(node),
        }
        self.tail = Some(node);
        self.len += 1;
    }

    pub fn pop_front(&mut self) -> Option<i32> {
        self.head.map(|h| {
            // SAFETY: `h` was created by `Box::leak` in `alloc` and is unlinked below, so it's freed exactly once.
            let node = unsafe { Box::from_raw(h.as_ptr()) };
            self.head = node.next;
            match self.head {
                // SAFETY: the new head is a live node we own.
                Some(mut n) => unsafe { n.as_mut().prev = None },
                None => self.tail = None,
            }
            self.len -= 1;
            node.val
        })
    }

    pub fn pop_back(&mut self) -> Option<i32> {
        self.tail.map(|t| {
            // SAFETY: as in pop_front, mirrored.
            let node = unsafe { Box::from_raw(t.as_ptr()) };
            self.tail = node.prev;
            match self.tail {
                // SAFETY: the new tail is a live node we own.
                Some(mut p) => unsafe { p.as_mut().next = None },
                None => self.head = None,
            }
            self.len -= 1;
            node.val
        })
    }

    pub fn len(&self) -> usize {
        self.len
    }

    pub fn is_empty(&self) -> bool {
        self.len == 0
    }

    pub fn iter(&self) -> Iter<'_> {
        Iter { next: self.head, _list: PhantomData }
    }
}

impl<'a> Iterator for Iter<'a> {
    type Item = &'a i32;

    fn next(&mut self) -> Option<&'a i32> {
        self.next.map(|n| {
            // SAFETY: the list is borrowed for 'a, so no node can be popped or freed while this reference lives.
            let node = unsafe { &*n.as_ptr() };
            self.next = node.next;
            &node.val
        })
    }
}

impl Drop for LinkedList {
    fn drop(&mut self) {
        while self.pop_front().is_some() {}
    }
}
"""

P.append(prob(
    "unsafe-doubly-linked-list", "Unsafe doubly linked list with NonNull", "hard", "beyond-box", ["unsafe", "NonNull", "Box::into_raw"],
    """
    Implement the same list with raw `NonNull` pointers: nodes are allocated with `Box` and owned by the list.
    Write a `// SAFETY:` comment on every `unsafe` block. `iter` yields `&i32` tied to the list's lifetime, and
    dropping the list frees every node without recursion. (Best attempted after Y2 Unsafe Rust.)
    """,
    NN_STARTER.strip("\n") + """

impl Default for LinkedList {
    fn default() -> Self {
        LinkedList { head: None, tail: None, len: 0, _owns: PhantomData }
    }
}

impl LinkedList {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn push_front(&mut self, val: i32) {
        todo!()
    }

    pub fn push_back(&mut self, val: i32) {
        todo!()
    }

    pub fn pop_front(&mut self) -> Option<i32> {
        todo!()
    }

    pub fn pop_back(&mut self) -> Option<i32> {
        todo!()
    }

    pub fn len(&self) -> usize {
        self.len
    }

    pub fn is_empty(&self) -> bool {
        self.len == 0
    }

    pub fn iter(&self) -> Iter<'_> {
        Iter { next: self.head, _list: PhantomData }
    }
}

impl<'a> Iterator for Iter<'a> {
    type Item = &'a i32;

    fn next(&mut self) -> Option<&'a i32> {
        todo!()
    }
}
""",
    NN_SOLUTION,
    [T("both_ends", "push_back 1,2; push_front 0; pop_back, pop_front", "(l.pop_back(), l.pop_front(), l.len())", "(Some(2), Some(0), 1)",
       setup="let mut l = LinkedList::new();\nl.push_back(1);\nl.push_back(2);\nl.push_front(0);"),
     T("iter", "push_back 1..=4", "l.iter().copied().collect::<Vec<_>>()", "vec![1, 2, 3, 4]",
       setup="let mut l = LinkedList::new();\nfor i in 1..=4 {\n    l.push_back(i);\n}"),
     T("empty", "new list", "(l.pop_front(), l.pop_back(), l.iter().next(), l.is_empty())", "(None, None, None, true)", setup="let mut l = LinkedList::new();"),
     T("single_both_ways", "push 5; pop_back; push 6; pop_front", "{ l.push_front(5); let a = l.pop_back(); l.push_back(6); (a, l.pop_front(), l.is_empty(), l.iter().count()) }", "(Some(5), Some(6), true, 0)",
       setup="let mut l = LinkedList::new();"),
     T("pushed_front_popped_back", "push_front 1, 2, 3; pop_back three times", "(l.pop_back(), l.pop_back(), l.pop_back(), l.len())", "(Some(1), Some(2), Some(3), 0)",
       setup="let mut l = LinkedList::new();\nl.push_front(1);\nl.push_front(2);\nl.push_front(3);")],
    [T("empty", "new list", "(l.pop_front(), l.pop_back(), l.iter().next(), l.is_empty())", "(None, None, None, true)", setup="let mut l = LinkedList::new();"),
     T("iter_after_pops", "push_back 0..6; pop_front, pop_back; iter", "{ l.pop_front(); l.pop_back(); l.iter().copied().collect::<Vec<_>>() }", "vec![1, 2, 3, 4]",
       setup="let mut l = LinkedList::new();\nfor i in 0..6 {\n    l.push_back(i);\n}"),
     T("len_tracks", "push 3, pop 1", "{ l.push_back(1); l.push_front(0); l.push_back(2); l.pop_front(); (l.len(), l.is_empty()) }", "(2, false)",
       setup="let mut l = LinkedList::new();"),
     T("extremes", "push i32::MIN front, i32::MAX back", "l.iter().copied().collect::<Vec<_>>()", "vec![i32::MIN, i32::MAX]",
       setup="let mut l = LinkedList::new();\nl.push_back(i32::MAX);\nl.push_front(i32::MIN);"),
     T("two_iters", "two iterators over the same list at once", "l.iter().zip(l.iter().skip(1)).map(|(a, b)| a + b).collect::<Vec<_>>()", "vec![3, 5]",
       setup="let mut l = LinkedList::new();\nfor i in 1..=3 {\n    l.push_back(i);\n}"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(515);
         for _ in 0..300 {
             let mut l = LinkedList::new();
             let mut model = std::collections::VecDeque::new();
             let mut ops: Vec<String> = Vec::new();
             for _ in 0..12 {
                 let x = rng.int(-9, 9) as i32;
                 match rng.below(4) {
                     0 => {
                         l.push_front(x);
                         model.push_front(x);
                         ops.push(format!("push_front {x}"));
                     }
                     1 => {
                         l.push_back(x);
                         model.push_back(x);
                         ops.push(format!("push_back {x}"));
                     }
                     2 => {
                         ops.push("pop_front".into());
                         check!(format!("{ops:?}"), l.pop_front(), model.pop_front());
                     }
                     _ => {
                         ops.push("pop_back".into());
                         check!(format!("{ops:?}"), l.pop_back(), model.pop_back());
                     }
                 }
                 check!(format!("{ops:?}: contents"), (l.iter().copied().collect::<Vec<_>>(), l.len()), (model.iter().copied().collect::<Vec<_>>(), model.len()));
             }
         }
     }
     """,
     T("single_both_ways", "push 5; pop_back; push 6; pop_front", "{ l.push_front(5); let a = l.pop_back(); l.push_back(6); (a, l.pop_front(), l.is_empty(), l.iter().count()) }", "(Some(5), Some(6), true, 0)",
       setup="let mut l = LinkedList::new();"),
     T("alternating", "push front/back alternately, 0..6", "l.iter().copied().collect::<Vec<_>>()", "vec![4, 2, 0, 1, 3, 5]",
       setup="let mut l = LinkedList::new();\nfor i in 0..6 {\n    if i % 2 == 0 { l.push_front(i) } else { l.push_back(i) }\n}"),
     T("big_drop", "push 10⁶ then drop", "l.len()", "1_000_000", setup="let mut l = LinkedList::new();\nfor i in 0..1_000_000 {\n    l.push_back(i);\n}")],
    [("rust", "Allocate with `NonNull::from(Box::leak(Box::new(node)))`; free with `unsafe { Box::from_raw(ptr.as_ptr()) }` exactly once, when the node is unlinked."),
     ("rust", "`PhantomData<Box<Node>>` says the list owns nodes; `PhantomData<&'a Node>` ties `Iter` to a borrow of the list."),
     ("approach", "Every `unsafe` block should be justified by an invariant: each node is owned by exactly one list and freed only in `pop_*`.")],
    ("This is how `std::collections::LinkedList` works. The safe API holds because `&mut self` gives exclusive access for mutation and `Iter<'a>` keeps the list borrowed while references exist.", "O(1) per op", "O(n)"),
    "Run the tests under Miri. What would it report if `pop_front` forgot to clear the new head's `prev`?",
    ["`NonNull` + `Box::leak`/`from_raw` ownership.", "`PhantomData` for ownership and lifetimes.", "`// SAFETY:` comments stating invariants."],
    related=["Y2", "S7"],
    wrong=dict(
        push_front_forgets_prev=NN_SOLUTION.replace("""            Some(mut h) => unsafe { h.as_mut().prev = Some(node) },
""", """            Some(_) => {}
"""),
        pop_front_forgets_len=NN_SOLUTION.replace("""                None => self.tail = None,
            }
            self.len -= 1;""", """                None => self.tail = None,
            }"""),
    ),
))

STAGES = [
    ("owned-lists", "Owned lists", "easy"),
    ("cursors", "Cursors", "medium"),
    ("beyond-box", "Beyond Box", "hard"),
]

if __name__ == "__main__":
    n = write_track("d5-linked-lists", "D5", "Linked lists", "D", "core", 5,
                    "`Option<Box<Node>>`, `take()` and `&mut` cursors; arenas for cycles; and why doubly linked lists need `Rc`/`Weak` or `unsafe` in Rust.",
                    STAGES, P)
    print("D5", n)

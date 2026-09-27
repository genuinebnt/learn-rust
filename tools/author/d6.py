from author import T, prob, write_track

# LeetCode's tree shape plus two helpers, shared by the Rc problems (given in both starter and solution).
TREE = """
use std::cell::RefCell;
use std::collections::VecDeque;
use std::rc::Rc;

#[derive(Debug, PartialEq, Eq)]
pub struct TreeNode {
    pub val: i32,
    pub left: Option<Rc<RefCell<TreeNode>>>,
    pub right: Option<Rc<RefCell<TreeNode>>>,
}

impl TreeNode {
    pub fn new(val: i32) -> Self {
        TreeNode { val, left: None, right: None }
    }
}

/// Builds a tree from LeetCode's level-order form: `None` is a missing child.
pub fn tree(values: &[Option<i32>]) -> Option<Rc<RefCell<TreeNode>>> {
    let mut it = values.iter();
    let root = Rc::new(RefCell::new(TreeNode::new((*it.next()?)?)));
    let mut queue = VecDeque::from([root.clone()]);
    while let Some(node) = queue.pop_front() {
        let n = &mut *node.borrow_mut();
        for child in [&mut n.left, &mut n.right] {
            match it.next() {
                None => return Some(root),
                Some(&Some(val)) => {
                    let c = Rc::new(RefCell::new(TreeNode::new(val)));
                    queue.push_back(c.clone());
                    *child = Some(c);
                }
                Some(None) => {}
            }
        }
    }
    Some(root)
}

/// The tree in LeetCode's level-order form, with trailing `None`s trimmed.
pub fn level_order_values(root: &Option<Rc<RefCell<TreeNode>>>) -> Vec<Option<i32>> {
    let mut out = Vec::new();
    let mut queue = VecDeque::from([root.clone()]);
    while let Some(slot) = queue.pop_front() {
        match slot {
            Some(node) => {
                let n = node.borrow();
                out.push(Some(n.val));
                queue.push_back(n.left.clone());
                queue.push_back(n.right.clone());
            }
            None => out.push(None),
        }
    }
    while out.last() == Some(&None) {
        out.pop();
    }
    out
}
"""


def with_tree(body: str) -> str:
    return TREE.strip("\n") + "\n\n" + body.strip("\n") + "\n"


# Test-side helpers for the Rc problems' hidden tests.
HELP = """
use std::cell::RefCell;
use std::rc::Rc;

/// Runs `f` on a thread with a 256 MB stack, for trees too deep for the default 2 MB.
#[allow(dead_code)]
fn big_stack<R: Send + 'static>(f: impl FnOnce() -> R + Send + 'static) -> R {
    std::thread::Builder::new().stack_size(256 << 20).spawn(f).unwrap().join().unwrap()
}

/// A random tree shape with `n` nodes and values in `lo..=hi`.
#[allow(dead_code)]
fn random_tree(rng: &mut anneal_prelude::Rng, n: usize, lo: i64, hi: i64) -> Option<Rc<RefCell<TreeNode>>> {
    if n == 0 {
        return None;
    }
    let v = rng.int(lo, hi) as i32;
    let root = Rc::new(RefCell::new(TreeNode::new(v)));
    let mut open = vec![(root.clone(), true), (root.clone(), false)];
    for _ in 1..n {
        let i = rng.below(open.len());
        let (parent, left) = open.swap_remove(i);
        let v = rng.int(lo, hi) as i32;
        let child = Rc::new(RefCell::new(TreeNode::new(v)));
        if left {
            parent.borrow_mut().left = Some(child.clone());
        } else {
            parent.borrow_mut().right = Some(child.clone());
        }
        open.push((child.clone(), true));
        open.push((child, false));
    }
    Some(root)
}

/// A path of `n` nodes valued 1..=n from the top, each the left (or right) child of the one above.
#[allow(dead_code)]
fn path(n: usize, left: bool) -> Option<Rc<RefCell<TreeNode>>> {
    let mut below = None;
    for v in (1..=n as i32).rev() {
        let mut node = TreeNode::new(v);
        if left {
            node.left = below;
        } else {
            node.right = below;
        }
        below = Some(Rc::new(RefCell::new(node)));
    }
    below
}

/// The complete tree with values 1..=n in level order.
#[allow(dead_code)]
fn complete(n: usize) -> Option<Rc<RefCell<TreeNode>>> {
    tree(&(1..=n as i32).map(Some).collect::<Vec<_>>())
}

/// LeetCode's text form, e.g. `[3,9,20,null,null,15,7]`.
#[allow(dead_code)]
fn show(root: &Option<Rc<RefCell<TreeNode>>>) -> String {
    let parts: Vec<String> = level_order_values(root).iter().map(|v| v.map_or("null".to_string(), |x| x.to_string())).collect();
    format!("[{}]", parts.join(","))
}
"""


def _items(s):
    s = s.strip()
    assert s[0] == "[" and s[-1] == "]", s
    body = s[1:-1].strip()
    return [x.strip() for x in body.split(",")] if body else []


def _opt(x):
    return "None" if x == "null" else f"Some({x})"


def tr(s):
    """`[3,9,null]` → `tree(&[Some(3), Some(9), None])`."""
    return "tree(&[" + ", ".join(_opt(x) for x in _items(s)) + "])"


def lo(s):
    """`[3,9,null,1]` → `vec![Some(3), Some(9), None, Some(1)]`."""
    items = _items(s)
    return "vec![" + ", ".join(_opt(x) for x in items) + "]" if items else "Vec::<Option<i32>>::new()"


RC = "Option<Rc<RefCell<TreeNode>>>"

P = []

# ---------------------------------------------------------------- basics (easy)

P.append(prob(
    "max-depth", "Maximum depth of binary tree", "easy", "basics", ["recursion", "Rc<RefCell>", "Blind 75"],
    "Return the number of nodes on the longest path from the root down to a leaf. An empty tree has depth 0.",
    with_tree("""
pub fn max_depth(root: Option<Rc<RefCell<TreeNode>>>) -> usize {
    todo!()
}
"""),
    with_tree("""
pub fn max_depth(root: Option<Rc<RefCell<TreeNode>>>) -> usize {
    match root {
        None => 0,
        Some(node) => {
            let n = node.borrow();
            1 + max_depth(n.left.clone()).max(max_depth(n.right.clone()))
        }
    }
}
"""),
    [T("leetcode_example", "root = [3,9,20,null,null,15,7]", f"max_depth({tr('[3,9,20,null,null,15,7]')})", "3"),
     T("leetcode_right_child", "root = [1,null,2]", f"max_depth({tr('[1,null,2]')})", "2"),
     T("empty", "root = []", "max_depth(None)", "0"),
     T("single", "root = [1]", f"max_depth({tr('[1]')})", "1"),
     T("deepest_leaf_on_the_right", "root = [1,2,3,null,null,4,null,null,5]", f"max_depth({tr('[1,2,3,null,null,4,null,null,5]')})", "4")],
    [T("left_path", "root = [1,2,null,3,null,4]", f"max_depth({tr('[1,2,null,3,null,4]')})", "4"),
     T("single_negative", "root = [-5]", f"max_depth({tr('[-5]')})", "1"),
     T("perfect_seven", "root = [1,2,3,4,5,6,7]", f"max_depth({tr('[1,2,3,4,5,6,7]')})", "3"),
     T("right_path", "root = [1,null,2,null,3]", f"max_depth({tr('[1,null,2,null,3]')})", "3"),
     T("zigzag", "root = [1,2,null,null,3,4]", f"max_depth({tr('[1,2,null,null,3,4]')})", "4"),
     T("extremes", "root = [i32::MIN,i32::MAX]", f"max_depth({tr('[i32::MIN,i32::MAX]')})", "2"),
     T("two_children", "root = [0,0,0]", f"max_depth({tr('[0,0,0]')})", "2"),
     T("short_left_long_right", "root = [1,2,3,null,null,null,4,null,5]", f"max_depth({tr('[1,2,3,null,null,null,4,null,5]')})", "4"),
     HELP,
     """
     #[test]
     fn random_vs_brute_force() {
         // Count BFS levels.
         let levels = |root: &Option<Rc<RefCell<TreeNode>>>| {
             let mut level: Vec<Rc<RefCell<TreeNode>>> = root.iter().cloned().collect();
             let mut depth = 0;
             while !level.is_empty() {
                 depth += 1;
                 level = level.iter().flat_map(|n| {
                     let n = n.borrow();
                     [n.left.clone(), n.right.clone()]
                 }).flatten().collect();
             }
             depth
         };
         let mut rng = anneal_prelude::Rng::new(601);
         for _ in 0..300 {
             let n = rng.below(16);
             let root = random_tree(&mut rng, n, -9, 9);
             check!(format!("root = {}", show(&root)), max_depth(root.clone()), levels(&root));
         }
     }

     #[test]
     fn scale_perfect_131071() {
         check!("root = complete tree of 2^17 - 1 nodes", max_depth(complete((1 << 17) - 1)), 17);
     }

     #[test]
     fn scale_path_50000() {
         let got = big_stack(|| max_depth(path(50_000, false)));
         check!("root = a right-leaning path of 50000 nodes", got, 50_000);
     }
     """],
    [("approach", "The depth of a tree is 1 plus the larger depth of its two subtrees; an empty tree is 0."),
     ("rust", "`node.borrow()` gives a `Ref<TreeNode>`; `n.left.clone()` copies the `Rc` pointer (not the subtree) so you can recurse."),
     ("edge", "`None` is the base case, so a leaf gets `1 + max(0, 0) = 1` without a special case.")],
    ("Each call handles one node and trusts the recursive calls for its subtrees. Cloning an `Rc` bumps a counter; it never copies the tree.", "O(n)", "O(h) for the recursion, h = height"),
    "Write it iteratively with a `VecDeque`, counting levels. Which version handles a 10⁶-node path?",
    ["The base-case-plus-recursive-call shape of tree code.", "`Rc::clone` is a pointer copy; `borrow()` reads through the `RefCell`."],
    examples=[("root = [3,9,20,null,null,15,7]", "3")],
    constraints=["0 ≤ nodes ≤ 2·10⁵", "height ≤ 10⁵ (the tests give deep trees enough stack)"],
    related=["S7", "D9"],
    companies=["Amazon", "Google", "Microsoft", "Apple", "LinkedIn"],
    wrong=dict(
        left_spine_only=with_tree("""
pub fn max_depth(root: Option<Rc<RefCell<TreeNode>>>) -> usize {
    match root {
        None => 0,
        Some(node) => 1 + max_depth(node.borrow().left.clone()),
    }
}
"""),
        min_instead_of_max=with_tree("""
pub fn max_depth(root: Option<Rc<RefCell<TreeNode>>>) -> usize {
    match root {
        None => 0,
        Some(node) => {
            let n = node.borrow();
            1 + max_depth(n.left.clone()).min(max_depth(n.right.clone()))
        }
    }
}
"""),
    ),
))

P.append(prob(
    "min-depth", "Minimum depth of binary tree", "easy", "basics", ["recursion", "BFS"],
    """
    Return the number of nodes on the shortest path from the root down to a **leaf** (a node with no children).
    An empty tree has depth 0.
    """,
    with_tree("""
pub fn min_depth(root: Option<Rc<RefCell<TreeNode>>>) -> usize {
    todo!()
}
"""),
    with_tree("""
pub fn min_depth(root: Option<Rc<RefCell<TreeNode>>>) -> usize {
    let Some(node) = root else { return 0 };
    let n = node.borrow();
    match (n.left.clone(), n.right.clone()) {
        (None, None) => 1,
        // A node with one child is not a leaf: the path has to go through that child.
        (Some(child), None) | (None, Some(child)) => 1 + min_depth(Some(child)),
        (left, right) => 1 + min_depth(left).min(min_depth(right)),
    }
}
"""),
    [T("leetcode_example", "root = [3,9,20,null,null,15,7]", f"min_depth({tr('[3,9,20,null,null,15,7]')})", "2"),
     T("leetcode_right_path", "root = [2,null,3,null,4,null,5,null,6]", f"min_depth({tr('[2,null,3,null,4,null,5,null,6]')})", "5"),
     T("empty", "root = []", "min_depth(None)", "0"),
     T("single", "root = [1]", f"min_depth({tr('[1]')})", "1"),
     T("one_child_is_not_a_leaf", "root = [1,2]", f"min_depth({tr('[1,2]')})", "2")],
    [T("leaf_on_the_right", "root = [1,2,3,4]", f"min_depth({tr('[1,2,3,4]')})", "2"),
     T("right_child_only", "root = [1,null,2]", f"min_depth({tr('[1,null,2]')})", "2"),
     T("perfect_seven", "root = [1,2,3,4,5,6,7]", f"min_depth({tr('[1,2,3,4,5,6,7]')})", "3"),
     T("left_path", "root = [1,2,null,3]", f"min_depth({tr('[1,2,null,3]')})", "3"),
     T("shallow_left_leaf", "root = [1,2,3,null,null,4,5]", f"min_depth({tr('[1,2,3,null,null,4,5]')})", "2"),
     T("negatives", "root = [-1,-2]", f"min_depth({tr('[-1,-2]')})", "2"),
     T("one_child_below_a_fork", "root = [1,2,3,4,null,null,5,6,null,null,7]", f"min_depth({tr('[1,2,3,4,null,null,5,6,null,null,7]')})", "4"),
     T("deep_leaf_only_on_one_side", "root = [1,null,2,3]", f"min_depth({tr('[1,null,2,3]')})", "3"),
     HELP,
     """
     #[test]
     fn random_vs_brute_force() {
         // BFS down to the first node with no children.
         let first_leaf = |root: &Option<Rc<RefCell<TreeNode>>>| {
             let mut level: Vec<Rc<RefCell<TreeNode>>> = root.iter().cloned().collect();
             let mut depth = 0;
             while !level.is_empty() {
                 depth += 1;
                 if level.iter().any(|n| n.borrow().left.is_none() && n.borrow().right.is_none()) {
                     return depth;
                 }
                 level = level.iter().flat_map(|n| {
                     let n = n.borrow();
                     [n.left.clone(), n.right.clone()]
                 }).flatten().collect();
             }
             depth
         };
         let mut rng = anneal_prelude::Rng::new(602);
         for _ in 0..300 {
             let n = rng.below(16);
             let root = random_tree(&mut rng, n, -9, 9);
             check!(format!("root = {}", show(&root)), min_depth(root.clone()), first_leaf(&root));
         }
     }

     #[test]
     fn scale_perfect_131071() {
         check!("root = complete tree of 2^17 - 1 nodes", min_depth(complete((1 << 17) - 1)), 17);
     }

     #[test]
     fn scale_path_50000() {
         let got = big_stack(|| {
             let long = path(50_000, true);
             let root = Some(Rc::new(RefCell::new(TreeNode { val: 0, left: None, right: long.clone() })));
             (min_depth(long), min_depth(root))
         });
         check!("a left path of 50000 nodes; then the same path as the right child of a root with no left child", got, (50_000, 50_001));
     }
     """],
    [("approach", "It looks like `max_depth` with `min`, but a missing child is not a leaf: `min(0, …)` would stop there."),
     ("rust", "Match on `(n.left.clone(), n.right.clone())` and handle the one-child cases separately."),
     ("edge", "`[1,2]` has depth 2: the root has a child, so it isn't a leaf.")],
    ("Only nodes with no children end a path. When one child is missing, the path must continue through the other; BFS finds the first leaf level and can stop early.", "O(n)", "O(h)"),
    "Why can BFS stop earlier than DFS here, and when does that matter?",
    ["A missing child is not a leaf.", "Matching on a tuple of `Option`s."],
    examples=[("root = [3,9,20,null,null,15,7]", "2")],
    constraints=["0 ≤ nodes ≤ 2·10⁵", "height ≤ 10⁵"],
    related=["D9"],
    companies=["Amazon", "Meta", "Microsoft"],
    wrong=dict(
        missing_child_counts_as_leaf=with_tree("""
pub fn min_depth(root: Option<Rc<RefCell<TreeNode>>>) -> usize {
    match root {
        None => 0,
        Some(node) => {
            let n = node.borrow();
            1 + min_depth(n.left.clone()).min(min_depth(n.right.clone()))
        }
    }
}
"""),
    ),
))

P.append(prob(
    "same-tree", "Same tree", "easy", "basics", ["recursion", "Blind 75"],
    "Return `true` if `p` and `q` have the same shape and the same value in every node.",
    with_tree("""
pub fn is_same_tree(p: Option<Rc<RefCell<TreeNode>>>, q: Option<Rc<RefCell<TreeNode>>>) -> bool {
    todo!()
}
"""),
    with_tree("""
pub fn is_same_tree(p: Option<Rc<RefCell<TreeNode>>>, q: Option<Rc<RefCell<TreeNode>>>) -> bool {
    match (p, q) {
        (None, None) => true,
        (Some(a), Some(b)) => {
            let (a, b) = (a.borrow(), b.borrow());
            a.val == b.val && is_same_tree(a.left.clone(), b.left.clone()) && is_same_tree(a.right.clone(), b.right.clone())
        }
        _ => false,
    }
}
"""),
    [T("leetcode_same", "p = [1,2,3], q = [1,2,3]", f"is_same_tree({tr('[1,2,3]')}, {tr('[1,2,3]')})", "true"),
     T("leetcode_shape_differs", "p = [1,2], q = [1,null,2]", f"is_same_tree({tr('[1,2]')}, {tr('[1,null,2]')})", "false"),
     T("leetcode_values_differ", "p = [1,2,1], q = [1,1,2]", f"is_same_tree({tr('[1,2,1]')}, {tr('[1,1,2]')})", "false"),
     T("both_empty", "p = [], q = []", "is_same_tree(None, None)", "true"),
     T("one_empty", "p = [], q = [1]", f"is_same_tree(None, {tr('[1]')})", "false")],
    [T("single_same", "p = [1], q = [1]", f"is_same_tree({tr('[1]')}, {tr('[1]')})", "true"),
     T("single_different", "p = [1], q = [2]", f"is_same_tree({tr('[1]')}, {tr('[2]')})", "false"),
     T("mirror_is_not_same", "p = [1,2,3], q = [1,3,2]", f"is_same_tree({tr('[1,2,3]')}, {tr('[1,3,2]')})", "false"),
     T("deep_shape_differs", "p = [1,2,3,4], q = [1,2,3,null,4]", f"is_same_tree({tr('[1,2,3,4]')}, {tr('[1,2,3,null,4]')})", "false"),
     T("extra_node_at_the_bottom", "p = [1,2,3], q = [1,2,3,null,null,null,4]", f"is_same_tree({tr('[1,2,3]')}, {tr('[1,2,3,null,null,null,4]')})", "false"),
     T("negatives_same", "p = [-1,-2,null,-3], q = [-1,-2,null,-3]", f"is_same_tree({tr('[-1,-2,null,-3]')}, {tr('[-1,-2,null,-3]')})", "true"),
     T("second_empty", "p = [0], q = []", f"is_same_tree({tr('[0]')}, None)", "false"),
     T("extremes", "p = [i32::MIN,null,i32::MAX], q = [i32::MIN,null,i32::MAX]", f"is_same_tree({tr('[i32::MIN,null,i32::MAX]')}, {tr('[i32::MIN,null,i32::MAX]')})", "true"),
     HELP,
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(603);
         for _ in 0..300 {
             let n = rng.below(8);
             let p = random_tree(&mut rng, n, 0, 2);
             // Half the time compare against an exact copy.
             let q = if rng.bool() { tree(&level_order_values(&p)) } else { let m = rng.below(8); random_tree(&mut rng, m, 0, 2) };
             let want = level_order_values(&p) == level_order_values(&q);
             check!(format!("p = {}, q = {}", show(&p), show(&q)), is_same_tree(p.clone(), q.clone()), want);
         }
     }

     #[test]
     fn scale_perfect_131071() {
         let n = (1 << 17) - 1;
         let mut values: Vec<Option<i32>> = (1..=n).map(Some).collect();
         let same = is_same_tree(tree(&values), tree(&values));
         values[n as usize - 1] = Some(0);
         let differs_last = is_same_tree(complete(n as usize), tree(&values));
         check!("two complete trees of 2^17 - 1 nodes, then the second with its last value changed", (same, differs_last), (true, false));
     }

     #[test]
     fn scale_paths_50000() {
         let got = big_stack(|| (is_same_tree(path(50_000, true), path(50_000, true)), is_same_tree(path(50_000, true), path(50_000, false))));
         check!("two left paths of 50000 nodes; a left path against a right path", got, (true, false));
     }
     """],
    [("approach", "Two trees are the same if both are empty, or both roots match and both pairs of subtrees are the same."),
     ("rust", "`match (p, q)` on the pair covers the four empty/non-empty cases at once.")],
    ("Comparing shape and value together in one recursion stops at the first difference. Comparing traversals needs null markers, or `[1,2]` and `[1,null,2]` look equal.", "O(n)", "O(h)"),
    "`#[derive(PartialEq)]` on `TreeNode` already compares whole trees. What does it do under the hood, and when would it be a bad idea on huge trees?",
    ["Matching a pair of `Option`s.", "Shape matters, not only the values."],
    examples=[("p = [1,2,3], q = [1,2,3]", "true")],
    constraints=["0 ≤ nodes ≤ 2·10⁵ per tree", "height ≤ 10⁵"],
    related=["S7"],
    companies=["Amazon", "Microsoft", "Bloomberg"],
    wrong=dict(
        preorder_values_only=with_tree("""
fn pre(node: &Option<Rc<RefCell<TreeNode>>>, out: &mut Vec<i32>) {
    if let Some(n) = node {
        let n = n.borrow();
        out.push(n.val);
        pre(&n.left, out);
        pre(&n.right, out);
    }
}

pub fn is_same_tree(p: Option<Rc<RefCell<TreeNode>>>, q: Option<Rc<RefCell<TreeNode>>>) -> bool {
    let (mut a, mut b) = (Vec::new(), Vec::new());
    pre(&p, &mut a);
    pre(&q, &mut b);
    a == b
}
"""),
        ignores_right=with_tree("""
pub fn is_same_tree(p: Option<Rc<RefCell<TreeNode>>>, q: Option<Rc<RefCell<TreeNode>>>) -> bool {
    match (p, q) {
        (None, None) => true,
        (Some(a), Some(b)) => {
            let (a, b) = (a.borrow(), b.borrow());
            a.val == b.val && is_same_tree(a.left.clone(), b.left.clone())
        }
        _ => false,
    }
}
"""),
    ),
))

P.append(prob(
    "invert-tree", "Invert binary tree", "easy", "basics", ["recursion", "borrow_mut", "Blind 75"],
    "Mirror the tree: swap the left and right child of every node. Return the root.",
    with_tree("""
pub fn invert_tree(root: Option<Rc<RefCell<TreeNode>>>) -> Option<Rc<RefCell<TreeNode>>> {
    todo!()
}
"""),
    with_tree("""
pub fn invert_tree(root: Option<Rc<RefCell<TreeNode>>>) -> Option<Rc<RefCell<TreeNode>>> {
    if let Some(node) = &root {
        let mut n = node.borrow_mut();
        // Swap the two fields in place, then fix each subtree.
        let n = &mut *n;
        std::mem::swap(&mut n.left, &mut n.right);
        invert_tree(n.left.clone());
        invert_tree(n.right.clone());
    }
    root
}
"""),
    [T("leetcode_example", "root = [4,2,7,1,3,6,9]", f"level_order_values(&invert_tree({tr('[4,2,7,1,3,6,9]')}))", lo("[4,7,2,9,6,3,1]")),
     T("leetcode_three", "root = [2,1,3]", f"level_order_values(&invert_tree({tr('[2,1,3]')}))", lo("[2,3,1]")),
     T("empty", "root = []", "invert_tree(None)", "None"),
     T("single", "root = [1]", f"level_order_values(&invert_tree({tr('[1]')}))", lo("[1]")),
     T("left_child_moves_right", "root = [1,2]", f"level_order_values(&invert_tree({tr('[1,2]')}))", lo("[1,null,2]"))],
    [T("right_child_moves_left", "root = [1,null,2]", f"level_order_values(&invert_tree({tr('[1,null,2]')}))", lo("[1,2]")),
     T("every_level_swaps", "root = [1,2,3,4,5]", f"level_order_values(&invert_tree({tr('[1,2,3,4,5]')}))", lo("[1,3,2,null,null,5,4]")),
     T("twice_is_identity", "root = [5,3,8,1,4,null,9] inverted twice", f"level_order_values(&invert_tree(invert_tree({tr('[5,3,8,1,4,null,9]')})))", lo("[5,3,8,1,4,null,9]")),
     T("negatives", "root = [-1,-2,-3,null,-4]", f"level_order_values(&invert_tree({tr('[-1,-2,-3,null,-4]')}))", lo("[-1,-3,-2,null,null,-4]")),
     T("four_levels", "root = [1,2,null,3,null,4]", f"level_order_values(&invert_tree({tr('[1,2,null,3,null,4]')}))", lo("[1,null,2,null,3,null,4]")),
     T("same_values", "root = [7,7,7,7]", f"level_order_values(&invert_tree({tr('[7,7,7,7]')}))", lo("[7,7,7,null,null,null,7]")),
     T("returns_the_same_root", "root = [1,2,3]", "Rc::ptr_eq(&root.clone().unwrap(), &invert_tree(root.clone()).unwrap())", "true", setup=f"let root = {tr('[1,2,3]')};"),
     T("extremes", "root = [0,i32::MIN,i32::MAX]", f"level_order_values(&invert_tree({tr('[0,i32::MIN,i32::MAX]')}))", lo("[0,i32::MAX,i32::MIN]")),
     HELP,
     """
     #[test]
     fn random_vs_brute_force() {
         // Build a mirrored copy with new nodes.
         fn mirror(node: &Option<Rc<RefCell<TreeNode>>>) -> Option<Rc<RefCell<TreeNode>>> {
             node.as_ref().map(|n| {
                 let n = n.borrow();
                 Rc::new(RefCell::new(TreeNode { val: n.val, left: mirror(&n.right), right: mirror(&n.left) }))
             })
         }
         let mut rng = anneal_prelude::Rng::new(604);
         for _ in 0..300 {
             let n = rng.below(16);
             let root = random_tree(&mut rng, n, -9, 9);
             let (input, want) = (show(&root), level_order_values(&mirror(&root)));
             check!(format!("root = {input}"), level_order_values(&invert_tree(root)), want);
         }
     }

     #[test]
     fn scale_perfect_131071() {
         let n: i32 = (1 << 17) - 1;
         // Each level of a mirrored complete tree is that level reversed.
         let mut want = Vec::new();
         for d in 0..17 {
             want.extend((1 << d..1 << (d + 1)).rev().map(Some));
         }
         check!("root = complete tree of 2^17 - 1 nodes", level_order_values(&invert_tree(complete(n as usize))) == want, true);
     }

     #[test]
     fn scale_path_50000() {
         let got = big_stack(|| {
             let mut node = invert_tree(path(50_000, true));
             let mut count = 0;
             while let Some(n) = node {
                 assert!(n.borrow().left.is_none());
                 count += 1;
                 node = n.borrow().right.clone();
             }
             count
         });
         check!("root = a left path of 50000 nodes (expect a right path)", got, 50_000);
     }
     """],
    [("approach", "Swap the root's two children, then invert each subtree. The order doesn't matter as long as both get inverted."),
     ("rust", "`std::mem::swap(&mut n.left, &mut n.right)` swaps two fields of the same `RefMut`; reborrow it as `&mut *n` first so both field borrows are allowed."),
     ("edge", "Return the same `root` you were given; inverting changes the nodes it points to, not the root pointer.")],
    ("The `RefCell` gives mutable access through a shared `Rc`. Swapping the `Option`s moves two pointers, no subtree is copied.", "O(n)", "O(h)"),
    "Write it iteratively with a queue. Does the order you visit nodes in matter?",
    ["`borrow_mut()` to change a node behind an `Rc`.", "`mem::swap` on two fields of the same struct."],
    examples=[("root = [4,2,7,1,3,6,9]", "[4,7,2,9,6,3,1]")],
    constraints=["0 ≤ nodes ≤ 2·10⁵", "height ≤ 10⁵"],
    related=["S7", "L2"],
    companies=["Google", "Amazon", "Meta", "Microsoft"],
    wrong=dict(
        root_only=with_tree("""
pub fn invert_tree(root: Option<Rc<RefCell<TreeNode>>>) -> Option<Rc<RefCell<TreeNode>>> {
    if let Some(node) = &root {
        let n = &mut *node.borrow_mut();
        std::mem::swap(&mut n.left, &mut n.right);
    }
    root
}
"""),
        overwrites_left_first=with_tree("""
pub fn invert_tree(root: Option<Rc<RefCell<TreeNode>>>) -> Option<Rc<RefCell<TreeNode>>> {
    if let Some(node) = &root {
        let mut n = node.borrow_mut();
        n.left = invert_tree(n.right.clone());
        n.right = invert_tree(n.left.clone());
    }
    root
}
"""),
    ),
))

P.append(prob(
    "symmetric-tree", "Symmetric tree", "easy", "basics", ["recursion", "mirror"],
    "Return `true` if the tree is a mirror image of itself around its centre.",
    with_tree("""
pub fn is_symmetric(root: Option<Rc<RefCell<TreeNode>>>) -> bool {
    todo!()
}
"""),
    with_tree("""
fn mirror(a: &Option<Rc<RefCell<TreeNode>>>, b: &Option<Rc<RefCell<TreeNode>>>) -> bool {
    match (a, b) {
        (None, None) => true,
        (Some(a), Some(b)) => {
            let (a, b) = (a.borrow(), b.borrow());
            // Outer pair and inner pair must mirror each other.
            a.val == b.val && mirror(&a.left, &b.right) && mirror(&a.right, &b.left)
        }
        _ => false,
    }
}

pub fn is_symmetric(root: Option<Rc<RefCell<TreeNode>>>) -> bool {
    match root {
        None => true,
        Some(node) => {
            let n = node.borrow();
            mirror(&n.left, &n.right)
        }
    }
}
"""),
    [T("leetcode_symmetric", "root = [1,2,2,3,4,4,3]", f"is_symmetric({tr('[1,2,2,3,4,4,3]')})", "true"),
     T("leetcode_not_symmetric", "root = [1,2,2,null,3,null,3]", f"is_symmetric({tr('[1,2,2,null,3,null,3]')})", "false"),
     T("empty", "root = []", "is_symmetric(None)", "true"),
     T("single", "root = [1]", f"is_symmetric({tr('[1]')})", "true"),
     T("values_differ", "root = [1,2,3]", f"is_symmetric({tr('[1,2,3]')})", "false")],
    [T("inorder_palindrome_trap", "root = [1,2,2,2,null,2]", f"is_symmetric({tr('[1,2,2,2,null,2]')})", "false"),
     T("inner_children_mirror", "root = [1,2,2,null,3,3]", f"is_symmetric({tr('[1,2,2,null,3,3]')})", "true"),
     T("one_child", "root = [1,2]", f"is_symmetric({tr('[1,2]')})", "false"),
     T("negatives", "root = [1,-2,-2]", f"is_symmetric({tr('[1,-2,-2]')})", "true"),
     T("outer_children_mirror", "root = [1,2,2,3,null,null,3]", f"is_symmetric({tr('[1,2,2,3,null,null,3]')})", "true"),
     T("four_levels", "root = [1,2,2,3,4,4,3,5,6,7,8,8,7,6,5]", f"is_symmetric({tr('[1,2,2,3,4,4,3,5,6,7,8,8,7,6,5]')})", "true"),
     T("equal_halves_are_not_mirrors", "root = [1,2,2,3,4,3,4]", f"is_symmetric({tr('[1,2,2,3,4,3,4]')})", "false"),
     T("same_shape_values_differ_deep", "root = [1,2,2,3,4,4,5]", f"is_symmetric({tr('[1,2,2,3,4,4,5]')})", "false"),
     HELP,
     """
     /// A copy with left and right swapped everywhere.
     fn mirrored(node: &Option<Rc<RefCell<TreeNode>>>) -> Option<Rc<RefCell<TreeNode>>> {
         node.as_ref().map(|n| {
             let n = n.borrow();
             Rc::new(RefCell::new(TreeNode { val: n.val, left: mirrored(&n.right), right: mirrored(&n.left) }))
         })
     }

     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(605);
         for _ in 0..300 {
             let n = rng.below(7);
             let half = random_tree(&mut rng, n, 0, 2);
             // Half the time build a symmetric tree, sometimes with one value nudged.
             let right = if rng.bool() { mirrored(&half) } else { let m = rng.below(7); random_tree(&mut rng, m, 0, 2) };
             if rng.below(4) == 0 {
                 if let Some(r) = &right {
                     r.borrow_mut().val += 1;
                 }
             }
             let root = Some(Rc::new(RefCell::new(TreeNode { val: 0, left: half, right })));
             let want = level_order_values(&root) == level_order_values(&mirrored(&root));
             check!(format!("root = {}", show(&root)), is_symmetric(root.clone()), want);
         }
     }

     #[test]
     fn scale_perfect_131071() {
         // Every node on level d holds d, so the tree mirrors itself.
         let values: Vec<Option<i32>> = (0..17).flat_map(|d| std::iter::repeat(Some(d)).take(1 << d)).collect();
         let mut odd = values.clone();
         let last = odd.len() - 1;
         odd[last] = Some(99);
         check!("perfect tree of 2^17 - 1 nodes with value = depth; then its last value changed", (is_symmetric(tree(&values)), is_symmetric(tree(&odd))), (true, false));
     }

     #[test]
     fn scale_paths_50000() {
         let got = big_stack(|| {
             let root = Some(Rc::new(RefCell::new(TreeNode { val: 0, left: path(25_000, true), right: path(25_000, false) })));
             is_symmetric(root)
         });
         check!("root with a left path and a right path of 25000 nodes each", got, true);
     }
     """],
    [("approach", "Compare the left subtree with the right subtree as mirrors: outer children with outer, inner with inner."),
     ("rust", "A helper `fn mirror(a: &Option<…>, b: &Option<…>) -> bool` that matches on `(a, b)` reads like the definition."),
     ("edge", "An in-order palindrome is not enough: `[1,2,2,2,null,2]` reads `2 2 1 2 2` but isn't symmetric.")],
    ("Symmetry is a same-tree check between the left subtree and the mirror of the right one, so `mirror(a.left, b.right) && mirror(a.right, b.left)`.", "O(n)", "O(h)"),
    "Write it iteratively: what do you push onto the queue, and in which order?",
    ["Recursing on two trees at once.", "Why a traversal without null markers loses the shape."],
    examples=[("root = [1,2,2,3,4,4,3]", "true")],
    constraints=["0 ≤ nodes ≤ 2·10⁵", "height ≤ 10⁵"],
    related=["S7"],
    companies=["Amazon", "Microsoft", "LinkedIn", "Bloomberg"],
    wrong=dict(
        inorder_palindrome=with_tree("""
fn inorder(node: &Option<Rc<RefCell<TreeNode>>>, out: &mut Vec<i32>) {
    if let Some(n) = node {
        let n = n.borrow();
        inorder(&n.left, out);
        out.push(n.val);
        inorder(&n.right, out);
    }
}

pub fn is_symmetric(root: Option<Rc<RefCell<TreeNode>>>) -> bool {
    let mut v = Vec::new();
    inorder(&root, &mut v);
    v.iter().eq(v.iter().rev())
}
"""),
        halves_equal=with_tree("""
fn same(a: &Option<Rc<RefCell<TreeNode>>>, b: &Option<Rc<RefCell<TreeNode>>>) -> bool {
    match (a, b) {
        (None, None) => true,
        (Some(a), Some(b)) => {
            let (a, b) = (a.borrow(), b.borrow());
            a.val == b.val && same(&a.left, &b.left) && same(&a.right, &b.right)
        }
        _ => false,
    }
}

pub fn is_symmetric(root: Option<Rc<RefCell<TreeNode>>>) -> bool {
    match root {
        None => true,
        Some(node) => {
            let n = node.borrow();
            same(&n.left, &n.right)
        }
    }
}
"""),
    ),
))

P.append(prob(
    "path-sum", "Path sum", "easy", "basics", ["recursion", "root-to-leaf"],
    """
    Return `true` if some path from the root down to a **leaf** has values adding up to `target_sum`.
    Values can be negative. An empty tree has no paths.
    """,
    with_tree("""
pub fn has_path_sum(root: Option<Rc<RefCell<TreeNode>>>, target_sum: i32) -> bool {
    todo!()
}
"""),
    with_tree("""
pub fn has_path_sum(root: Option<Rc<RefCell<TreeNode>>>, target_sum: i32) -> bool {
    let Some(node) = root else { return false };
    let n = node.borrow();
    let rest = target_sum - n.val;
    if n.left.is_none() && n.right.is_none() {
        return rest == 0;
    }
    has_path_sum(n.left.clone(), rest) || has_path_sum(n.right.clone(), rest)
}
"""),
    [T("leetcode_example", "root = [5,4,8,11,null,13,4,7,2,null,null,null,1], target_sum = 22", f"has_path_sum({tr('[5,4,8,11,null,13,4,7,2,null,null,null,1]')}, 22)", "true"),
     T("leetcode_no_path", "root = [1,2,3], target_sum = 5", f"has_path_sum({tr('[1,2,3]')}, 5)", "false"),
     T("empty_has_no_path", "root = [], target_sum = 0", "has_path_sum(None, 0)", "false"),
     T("must_end_at_a_leaf", "root = [1,2], target_sum = 1", f"has_path_sum({tr('[1,2]')}, 1)", "false"),
     T("negatives", "root = [-2,null,-3], target_sum = -5", f"has_path_sum({tr('[-2,null,-3]')}, -5)", "true")],
    [T("single_match", "root = [1], target_sum = 1", f"has_path_sum({tr('[1]')}, 1)", "true"),
     T("single_miss", "root = [1], target_sum = 0", f"has_path_sum({tr('[1]')}, 0)", "false"),
     T("right_leaf", "root = [1,2,3], target_sum = 4", f"has_path_sum({tr('[1,2,3]')}, 4)", "true"),
     T("zeros_never_sum_to_zero", "root = [0,1,1], target_sum = 0", f"has_path_sum({tr('[0,1,1]')}, 0)", "false"),
     T("leetcode_negatives", "root = [1,-2,-3,1,3,-2,null,-1], target_sum = -1", f"has_path_sum({tr('[1,-2,-3,1,3,-2,null,-1]')}, -1)", "true"),
     T("overshoot_then_come_back", "root = [5,6,-4], target_sum = 1", f"has_path_sum({tr('[5,6,-4]')}, 1)", "true"),
     T("partial_path_does_not_count", "root = [1,2,null,3], target_sum = 3", f"has_path_sum({tr('[1,2,null,3]')}, 3)", "false"),
     T("single_zero", "root = [0], target_sum = 0", f"has_path_sum({tr('[0]')}, 0)", "true"),
     HELP,
     """
     #[test]
     fn random_vs_brute_force() {
         // Every root-to-leaf sum.
         fn sums(node: &Option<Rc<RefCell<TreeNode>>>, above: i32, out: &mut Vec<i32>) {
             if let Some(n) = node {
                 let n = n.borrow();
                 if n.left.is_none() && n.right.is_none() {
                     out.push(above + n.val);
                 }
                 sums(&n.left, above + n.val, out);
                 sums(&n.right, above + n.val, out);
             }
         }
         let mut rng = anneal_prelude::Rng::new(606);
         for _ in 0..400 {
             let n = rng.below(12);
             let root = random_tree(&mut rng, n, -5, 5);
             let target = rng.int(-8, 8) as i32;
             let mut all = Vec::new();
             sums(&root, 0, &mut all);
             check!(format!("root = {}, target_sum = {target}", show(&root)), has_path_sum(root.clone(), target), all.contains(&target));
         }
     }

     #[test]
     fn scale_perfect_131071() {
         // The leaf 131071 is reached through 1, 3, 7, 15, …, 2^k - 1.
         let sum: i32 = (1..=17).map(|k| (1 << k) - 1).sum();
         let root = complete((1 << 17) - 1);
         check!("root = complete tree of 2^17 - 1 nodes, target_sum = sum of the rightmost path, then one more", (has_path_sum(root.clone(), sum), has_path_sum(root, sum + 1)), (true, false));
     }

     #[test]
     fn scale_path_50000() {
         let got = big_stack(|| (has_path_sum(path(50_000, false), 1_250_025_000), has_path_sum(path(50_000, false), 1_250_024_999)));
         check!("root = right path 1..=50000, target_sum = 1250025000; then 1250024999", got, (true, false));
     }
     """],
    [("approach", "Subtract the node's value from the target and ask the same question of each child. At a leaf, check whether what's left is 0."),
     ("rust", "`let Some(node) = root else { return false };` handles the empty tree up front."),
     ("edge", "Values can be negative, so you can't stop early when the running sum passes the target.")],
    ("Passing the remaining target down turns the question into a leaf check. Only nodes with no children end a path.", "O(n)", "O(h)"),
    "Return every matching path instead of a `bool` (that's Path sum II, later in this track).",
    ["Carrying state down a recursion.", "Leaf means no children, not 'a missing child'."],
    examples=[("root = [5,4,8,11,null,13,4,7,2,null,null,null,1], target_sum = 22", "true")],
    constraints=["0 ≤ nodes ≤ 2·10⁵", "height ≤ 10⁵", "path sums fit in i32"],
    related=["S1"],
    companies=["Amazon", "Meta", "Microsoft"],
    wrong=dict(
        any_node_not_only_leaves=with_tree("""
pub fn has_path_sum(root: Option<Rc<RefCell<TreeNode>>>, target_sum: i32) -> bool {
    let Some(node) = root else { return false };
    let n = node.borrow();
    let rest = target_sum - n.val;
    rest == 0 || has_path_sum(n.left.clone(), rest) || has_path_sum(n.right.clone(), rest)
}
"""),
        prunes_on_overshoot=with_tree("""
pub fn has_path_sum(root: Option<Rc<RefCell<TreeNode>>>, target_sum: i32) -> bool {
    let Some(node) = root else { return false };
    let n = node.borrow();
    let rest = target_sum - n.val;
    if n.left.is_none() && n.right.is_none() {
        return rest == 0;
    }
    if target_sum > 0 && rest < 0 {
        return false;
    }
    has_path_sum(n.left.clone(), rest) || has_path_sum(n.right.clone(), rest)
}
"""),
        missing_child_ends_a_path=with_tree("""
pub fn has_path_sum(root: Option<Rc<RefCell<TreeNode>>>, target_sum: i32) -> bool {
    let Some(node) = root else { return target_sum == 0 };
    let n = node.borrow();
    let rest = target_sum - n.val;
    has_path_sum(n.left.clone(), rest) || has_path_sum(n.right.clone(), rest)
}
"""),
    ),
))

P.append(prob(
    "sorted-array-to-bst", "Convert sorted array to BST", "easy", "basics", ["divide and conquer", "slices", "BST"],
    """
    `nums` is sorted in strictly increasing order. Build a height-balanced binary search tree from it: the root is
    `nums[nums.len() / 2]`, its left subtree is built the same way from the elements before it, and its right
    subtree from the elements after it.
    """,
    with_tree("""
pub fn sorted_array_to_bst(nums: &[i32]) -> Option<Rc<RefCell<TreeNode>>> {
    todo!()
}
"""),
    with_tree("""
pub fn sorted_array_to_bst(nums: &[i32]) -> Option<Rc<RefCell<TreeNode>>> {
    if nums.is_empty() {
        return None;
    }
    let mid = nums.len() / 2;
    Some(Rc::new(RefCell::new(TreeNode {
        val: nums[mid],
        left: sorted_array_to_bst(&nums[..mid]),
        right: sorted_array_to_bst(&nums[mid + 1..]),
    })))
}
"""),
    [T("leetcode_example", "nums = [-10,-3,0,5,9]", "level_order_values(&sorted_array_to_bst(&[-10, -3, 0, 5, 9]))", lo("[0,-3,9,-10,null,5]")),
     T("leetcode_two", "nums = [1,3]", "level_order_values(&sorted_array_to_bst(&[1, 3]))", lo("[3,1]")),
     T("empty", "nums = []", "sorted_array_to_bst(&[])", "None"),
     T("single", "nums = [7]", "level_order_values(&sorted_array_to_bst(&[7]))", lo("[7]")),
     T("three", "nums = [1,2,3]", "level_order_values(&sorted_array_to_bst(&[1, 2, 3]))", lo("[2,1,3]"))],
    [T("four_takes_the_upper_middle", "nums = [1,2,3,4]", "level_order_values(&sorted_array_to_bst(&[1, 2, 3, 4]))", lo("[3,2,4,1]")),
     T("seven", "nums = [1,2,3,4,5,6,7]", "level_order_values(&sorted_array_to_bst(&[1, 2, 3, 4, 5, 6, 7]))", lo("[4,2,6,1,3,5,7]")),
     T("negatives", "nums = [-5,-4]", "level_order_values(&sorted_array_to_bst(&[-5, -4]))", lo("[-4,-5]")),
     T("extremes", "nums = [i32::MIN,0,i32::MAX]", "level_order_values(&sorted_array_to_bst(&[i32::MIN, 0, i32::MAX]))", lo("[0,i32::MIN,i32::MAX]")),
     T("five", "nums = [1,2,3,4,5]", "level_order_values(&sorted_array_to_bst(&[1, 2, 3, 4, 5]))", lo("[3,2,5,1,null,4]")),
     T("six", "nums = [1,2,3,4,5,6]", "level_order_values(&sorted_array_to_bst(&[1, 2, 3, 4, 5, 6]))", lo("[4,2,6,1,3,5]")),
     T("two_negative_one_positive", "nums = [-3,-1,2]", "level_order_values(&sorted_array_to_bst(&[-3, -1, 2]))", lo("[-1,-3,2]")),
     T("eight", "nums = [0,1,2,3,4,5,6,7]", "level_order_values(&sorted_array_to_bst(&[0, 1, 2, 3, 4, 5, 6, 7]))", lo("[4,2,6,1,3,5,7,0]")),
     """
     /// The expected level order, walking index ranges breadth first.
     fn by_ranges(nums: &[i32]) -> Vec<Option<i32>> {
         let mut out = Vec::new();
         let mut queue = std::collections::VecDeque::from([(0, nums.len())]);
         while let Some((lo, hi)) = queue.pop_front() {
             if lo == hi {
                 out.push(None);
                 continue;
             }
             let mid = lo + (hi - lo) / 2;
             out.push(Some(nums[mid]));
             queue.push_back((lo, mid));
             queue.push_back((mid + 1, hi));
         }
         while out.last() == Some(&None) {
             out.pop();
         }
         out
     }

     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(607);
         for _ in 0..300 {
             let n = rng.below(20);
             let mut nums: Vec<i32> = rng.vec(n, -50, 50);
             nums.sort();
             nums.dedup();
             check!(format!("nums = {nums:?}"), level_order_values(&sorted_array_to_bst(&nums)), by_ranges(&nums));
         }
     }

     #[test]
     fn scale_200000() {
         let nums: Vec<i32> = (0..200_000).map(|i| i * 3 - 300_000).collect();
         check!("nums = [-300000, -299997, …] (200000 values)", level_order_values(&sorted_array_to_bst(&nums)) == by_ranges(&nums), true);
     }
     """],
    [("approach", "Pick the middle element as the root; everything left of it goes in the left subtree, everything right of it in the right."),
     ("rust", "Recurse on sub-slices `&nums[..mid]` and `&nums[mid + 1..]`: no copying, no index bookkeeping."),
     ("edge", "For an even length, `len / 2` is the upper of the two middles: `[1,3]` gives root 3.")],
    ("Splitting at the middle keeps the two halves within one element of each other, so the tree is height-balanced; the sorted order makes it a BST.", "O(n)", "O(log n) recursion"),
    "Build the same tree from a sorted linked list without converting it to a `Vec` first.",
    ["Divide and conquer on sub-slices.", "Why picking the middle keeps the tree balanced."],
    examples=[("nums = [-10,-3,0,5,9]", "[0,-3,9,-10,null,5]")],
    constraints=["0 ≤ nums.len() ≤ 2·10⁵", "nums is strictly increasing"],
    related=["S3", "D4"],
    companies=["Amazon", "Google", "Microsoft"],
    wrong=dict(
        lower_middle=with_tree("""
pub fn sorted_array_to_bst(nums: &[i32]) -> Option<Rc<RefCell<TreeNode>>> {
    if nums.is_empty() {
        return None;
    }
    let mid = (nums.len() - 1) / 2;
    Some(Rc::new(RefCell::new(TreeNode {
        val: nums[mid],
        left: sorted_array_to_bst(&nums[..mid]),
        right: sorted_array_to_bst(&nums[mid + 1..]),
    })))
}
"""),
        chain=with_tree("""
pub fn sorted_array_to_bst(nums: &[i32]) -> Option<Rc<RefCell<TreeNode>>> {
    let (&first, rest) = nums.split_first()?;
    Some(Rc::new(RefCell::new(TreeNode { val: first, left: None, right: sorted_array_to_bst(rest) })))
}
"""),
    ),
))

P.append(prob(
    "fix-borrow-mut-error", "Fix: `BorrowMutError` in a tree walk", "easy", "basics", ["RefCell", "borrow_mut", "panic"],
    """
    `add_path_sums` should replace every value with the sum of the values on the path from the root down to that
    node. It panics with `already borrowed: BorrowMutError` instead. Make it work by changing how the node is
    borrowed (at most 3 changed lines).
    """,
    with_tree("""
/// Replaces each value with the sum of the values from the root down to that node.
pub fn add_path_sums(root: &Option<Rc<RefCell<TreeNode>>>) {
    walk(root, 0);
}

fn walk(slot: &Option<Rc<RefCell<TreeNode>>>, above: i32) {
    if let Some(node) = slot {
        let n = node.borrow();
        node.borrow_mut().val += above;
        walk(&n.left, n.val);
        walk(&n.right, n.val);
    }
}
"""),
    with_tree("""
/// Replaces each value with the sum of the values from the root down to that node.
pub fn add_path_sums(root: &Option<Rc<RefCell<TreeNode>>>) {
    walk(root, 0);
}

fn walk(slot: &Option<Rc<RefCell<TreeNode>>>, above: i32) {
    if let Some(node) = slot {
        let mut n = node.borrow_mut();
        n.val += above;
        walk(&n.left, n.val);
        walk(&n.right, n.val);
    }
}
"""),
    [T("three", "root = [1,2,3]", "level_order_values(&root)", lo("[1,3,4]"), setup=f"let root = {tr('[1,2,3]')};\nadd_path_sums(&root);"),
     T("empty", "root = []", "level_order_values(&root)", lo("[]"), setup="let root = tree(&[]);\nadd_path_sums(&root);"),
     T("single", "root = [5]", "level_order_values(&root)", lo("[5]"), setup=f"let root = {tr('[5]')};\nadd_path_sums(&root);"),
     T("sums_go_all_the_way_down", "root = [1,2,null,3]", "level_order_values(&root)", lo("[1,3,null,6]"), setup=f"let root = {tr('[1,2,null,3]')};\nadd_path_sums(&root);"),
     T("negatives", "root = [1,-1,-2,null,4]", "level_order_values(&root)", lo("[1,0,-1,null,4]"), setup=f"let root = {tr('[1,-1,-2,null,4]')};\nadd_path_sums(&root);")],
    [T("zeros", "root = [0,0,0]", "level_order_values(&root)", lo("[0,0,0]"), setup=f"let root = {tr('[0,0,0]')};\nadd_path_sums(&root);"),
     T("perfect_seven", "root = [1,2,3,4,5,6,7]", "level_order_values(&root)", lo("[1,3,4,7,8,10,11]"), setup=f"let root = {tr('[1,2,3,4,5,6,7]')};\nadd_path_sums(&root);"),
     T("cancels_out", "root = [10,null,-10,null,5]", "level_order_values(&root)", lo("[10,null,0,null,5]"), setup=f"let root = {tr('[10,null,-10,null,5]')};\nadd_path_sums(&root);"),
     T("single_negative", "root = [-3]", "level_order_values(&root)", lo("[-3]"), setup=f"let root = {tr('[-3]')};\nadd_path_sums(&root);"),
     T("siblings_are_independent", "root = [1,2,3,4,null,null,5]", "level_order_values(&root)", lo("[1,3,4,7,null,null,9]"), setup=f"let root = {tr('[1,2,3,4,null,null,5]')};\nadd_path_sums(&root);"),
     T("left_path", "root = [1,1,null,1,null,1]", "level_order_values(&root)", lo("[1,2,null,3,null,4]"), setup=f"let root = {tr('[1,1,null,1,null,1]')};\nadd_path_sums(&root);"),
     T("twice", "root = [1,2] summed twice", "level_order_values(&root)", lo("[1,4]"), setup=f"let root = {tr('[1,2]')};\nadd_path_sums(&root);\nadd_path_sums(&root);"),
     T("large_values", "root = [1000000,1000000,1000000]", "level_order_values(&root)", lo("[1000000,2000000,2000000]"), setup=f"let root = {tr('[1000000,1000000,1000000]')};\nadd_path_sums(&root);"),
     HELP,
     """
     /// The expected level order: BFS carrying the sum from the root.
     fn expected(root: &Option<Rc<RefCell<TreeNode>>>) -> Vec<Option<i32>> {
         let mut out = Vec::new();
         let mut queue = std::collections::VecDeque::from([(root.clone(), 0)]);
         while let Some((slot, above)) = queue.pop_front() {
             match slot {
                 Some(n) => {
                     let n = n.borrow();
                     out.push(Some(above + n.val));
                     queue.push_back((n.left.clone(), above + n.val));
                     queue.push_back((n.right.clone(), above + n.val));
                 }
                 None => out.push(None),
             }
         }
         while out.last() == Some(&None) {
             out.pop();
         }
         out
     }

     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(608);
         for _ in 0..300 {
             let n = rng.below(14);
             let root = random_tree(&mut rng, n, -9, 9);
             let (input, want) = (show(&root), expected(&root));
             add_path_sums(&root);
             check!(format!("root = {input}"), level_order_values(&root), want);
         }
     }

     #[test]
     fn scale_path_50000() {
         let got = big_stack(|| {
             let root = path(50_000, true);
             add_path_sums(&root);
             let mut node = root;
             let mut last = 0;
             while let Some(n) = node {
                 last = n.borrow().val;
                 node = n.borrow().left.clone();
             }
             last
         });
         check!("root = left path 1..=50000 (the bottom value becomes 1 + 2 + … + 50000)", got, 1_250_025_000);
     }
     """],
    [("rust", "`n` holds a shared `borrow()` of the node while `borrow_mut()` asks for an exclusive one on the same `RefCell`. That's the panic."),
     ("rust", "Take one `borrow_mut()` and use it for both the update and the reads that follow. Borrowing the children's cells while you hold the parent's is fine: they're different `RefCell`s.")],
    ("A `RefCell` checks the borrow rules at run time: any number of `borrow()`s or exactly one `borrow_mut()`, per cell. Holding one `RefMut` for the whole visit satisfies that, and each child has its own cell.", "O(n)", "O(h)"),
    "Would the same code work if you called `walk` on the children *after* dropping the `RefMut`? What would you have to clone?",
    ["`RefCell` borrow rules are checked per cell, at run time.", "One `borrow_mut()` scope instead of a `borrow()` and a `borrow_mut()` that overlap."],
    mode="fix", rules=dict(methods=["try_borrow_mut", "try_borrow", "as_ptr"], lines=3),
    examples=[("root = [1,2,3]", "[1,3,4]")],
    constraints=["0 ≤ nodes ≤ 10⁵", "path sums fit in i32"],
    related=["L2", "S7"],
    wrong=dict(
        skips_when_busy=with_tree("""
/// Replaces each value with the sum of the values from the root down to that node.
pub fn add_path_sums(root: &Option<Rc<RefCell<TreeNode>>>) {
    walk(root, 0);
}

fn walk(slot: &Option<Rc<RefCell<TreeNode>>>, above: i32) {
    if let Some(node) = slot {
        let n = node.borrow();
        if let Ok(mut m) = node.try_borrow_mut() {
            m.val += above;
        }
        walk(&n.left, n.val);
        walk(&n.right, n.val);
    }
}
"""),
        adds_parent_only=with_tree("""
/// Replaces each value with the sum of the values from the root down to that node.
pub fn add_path_sums(root: &Option<Rc<RefCell<TreeNode>>>) {
    walk(root, 0);
}

fn walk(slot: &Option<Rc<RefCell<TreeNode>>>, above: i32) {
    if let Some(node) = slot {
        let mut n = node.borrow_mut();
        let own = n.val;
        n.val += above;
        walk(&n.left, own);
        walk(&n.right, own);
    }
}
"""),
    ),
))

STAGES = [
    ("basics", "Basics", "easy"),
    ("traversals", "Traversals", "easy"),
    ("levels-recursion", "Levels & recursion", "medium"),
    ("bsts", "BSTs", "medium"),
    ("ownership-shaped-trees", "Ownership-shaped trees", "hard"),
]

if __name__ == "__main__":
    n = write_track("d6-trees-bsts", "D6", "Trees & BSTs", "D", "core", 6,
                    "LeetCode's `Option<Rc<RefCell<TreeNode>>>` trees: recursion, traversals, levels and BSTs; then trees shaped the Rust way with `Box`, arenas and `Weak`.",
                    STAGES, P)
    print("D6", n)

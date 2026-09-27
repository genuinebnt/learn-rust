use solution::*;

fn build(words: &[&str]) -> Node {
    let mut root = Node::default();
    for w in words {
        let mut cur = &mut root;
        for c in w.chars() {
            cur = cur.kids.entry(c).or_default();
        }
        cur.count += 1;
    }
    root
}

fn depth(root: &mut Node, path: &str) -> usize {
    let target: *const Node = deepest_mut(root, path);
    let mut cur: &Node = root;
    let mut d = 0;
    for c in path.chars() {
        if std::ptr::eq(cur, target) {
            return d;
        }
        match cur.kids.get(&c) {
            Some(next) => cur = next,
            None => return usize::MAX,
        }
        d += 1;
    }
    if std::ptr::eq(cur, target) { d } else { usize::MAX }
}

fn words(xs: &[&str]) -> Vec<String> {
    xs.iter().map(|s| s.to_string()).collect()
}

#[test]
fn deepest_example() {
    let mut root = build(&["car", "cat"]);
    check!(r#"trie {car, cat}; path "cart""#, depth(&mut root, "cart"), 3);
}

#[test]
fn deepest_missing_first() {
    let mut root = build(&["car"]);
    check!(r#"trie {car}; path "dog""#, depth(&mut root, "dog"), 0);
}

#[test]
fn grow_one_node_at_a_time() {
    let mut root = Node::default();
    check!(r#"trie {}; grow "ab" three times"#, (grow(&mut root, "ab").count, grow(&mut root, "ab").count, grow(&mut root, "ab").count), (1, 1, 2));
}

#[test]
fn first_long() {
    let mut v = words(&["a", "long", "longer"]);
    check!(r#"["a", "long", "longer"], n 2: append "!""#, { first_long_or_push(&mut v, 2).push('!'); v }, words(&["a", "long!", "longer"]));
}

#[test]
fn fallback() {
    let mut v = words(&["a"]);
    check!(r#"["a"], n 5: append "?""#, { first_long_or_push(&mut v, 5).push('?'); v }, words(&["a", "fallback?"]));
}

#[test]
fn empty_path() {
    let mut root = build(&["a"]);
    check!(r#"trie {a}; path """#, depth(&mut root, ""), 0);
}

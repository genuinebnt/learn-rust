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
fn full_path_exists() {
    let mut root = build(&["abc"]);
    check!(r#"trie {abc}; path "abc""#, depth(&mut root, "abc"), 3);
}

#[test]
fn deepest_is_mutable() {
    let mut root = build(&["ab"]);
    check!(r#"trie {ab}; deepest("abz").count += 5; then count of "ab""#, { deepest_mut(&mut root, "abz").count += 5; deepest_mut(&mut root, "ab").count }, 6);
}

#[test]
fn grow_existing_path() {
    let mut root = build(&["ab"]);
    check!(r#"trie {ab}; grow "ab""#, grow(&mut root, "ab").count, 2);
}

#[test]
fn grow_empty_path() {
    let mut root = Node::default();
    check!(r#"trie {}; grow """#, (grow(&mut root, "").count, root.kids.len()), (1, 0));
}

#[test]
fn unicode_path() {
    let mut root = build(&["日本"]);
    check!(r#"trie {日本}; path "日本語""#, depth(&mut root, "日本語"), 2);
}

#[test]
fn first_long_empty() {
    let mut v: Vec<String> = vec![];
    check!(r#"[], n 0"#, { first_long_or_push(&mut v, 0); v }, words(&["fallback"]));
}

#[test]
fn first_long_is_strict() {
    let mut v = words(&["ab"]);
    check!(r#"["ab"], n 2"#, { first_long_or_push(&mut v, 2); v }, words(&["ab", "fallback"]));
}

#[test]
fn first_long_is_first() {
    let mut v = words(&["xyz", "abc"]);
    check!(r#"["xyz", "abc"], n 1"#, { first_long_or_push(&mut v, 1).clear(); v }, words(&["", "abc"]));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6231);
    for _ in 0..300 {
        let mut owned = Vec::new();
        for _ in 0..rng.below(4) {
            owned.push(String::new());
        }
        for w in owned.iter_mut() {
            let len = 1 + (w.len() % 3);
            w.push_str(&"ab"[..len.min(2)]);
        }
        let refs: Vec<&str> = owned.iter().map(|s| s.as_str()).collect();
        let mut root = build(&refs);
        let len = rng.below(5);
        let path = rng.string(len, "ab");
        let mut want = 0;
        {
            let mut cur = &root;
            for c in path.chars() {
                match cur.kids.get(&c) {
                    Some(n) => {
                        cur = n;
                        want += 1;
                    }
                    None => break,
                }
            }
        }
        check!(format!("trie {refs:?}; path {path:?}"), depth(&mut root, &path), want);
        let before: u32 = grow(&mut root, &path).count;
        check!(format!("trie {refs:?}; grow {path:?}: count"), before >= 1, true);

        let n = rng.below(4);
        let mut v: Vec<String> = (0..rng.below(4)).map(|_| "x".repeat(rng.below(4))).collect();
        let start = v.clone();
        let mut want = v.clone();
        match want.iter().position(|w| w.len() > n) {
            Some(i) => want[i].push('!'),
            None => want.push("fallback!".to_string()),
        }
        first_long_or_push(&mut v, n).push('!');
        check!(format!("first_long_or_push({start:?}, {n})"), v, want);
    }
}

#[test]
fn deep_trie() {
    let path: String = "ab".repeat(5_000);
    let mut root = Node::default();
    for _ in 0..3 {
        grow(&mut root, &path[..100]);
    }
    let mut v: Vec<String> = (0..100_000).map(|i| if i == 99_999 { "long".to_string() } else { String::new() }).collect();
    first_long_or_push(&mut v, 3).push('!');
    check!("grow a 100-char path 3 times; then 100000 words, the long one last", (depth(&mut root, &path), v[99_999].clone(), v.len()), (3, "long!".to_string(), 100_000));
}

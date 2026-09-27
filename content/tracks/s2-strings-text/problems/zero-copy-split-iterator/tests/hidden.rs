use solution::*;

#[test]
fn trailing() {
    check!(r#""a,", ','"#, split_on("a,", ',').collect::<Vec<_>>(), vec!["a", ""]);
}

#[test]
fn reversed() {
    check!(r#""a,b,c", ',' reversed"#, split_on("a,b,c", ',').rev().collect::<Vec<_>>(), vec!["c", "b", "a"]);
}

#[test]
fn both_ends() {
    let mut it = split_on("1-2-3-4", '-');
    check!(r#""1-2-3-4": next, next_back, next, next_back, next"#, (it.next(), it.next_back(), it.next(), it.next_back(), it.next()), (Some("1"), Some("4"), Some("2"), Some("3"), None));
}

#[test]
fn unicode_delim() {
    check!(r#""x→y→", '→'"#, split_on("x→y→", '→').collect::<Vec<_>>(), vec!["x", "y", ""]);
}

#[test]
fn items_outlive_iterator() {
    let text = String::from("ab cd");
    let first;
    {
        let mut it = split_on(&text, ' ');
        first = it.next();
    }
    check!(r#"keep the first piece after dropping the iterator"#, first, Some("ab"));
}

#[test]
fn matches_std() {
    let s = ";;a;bc;;d;";
    let ours: Vec<&str> = split_on(s, ';').collect();
    let theirs: Vec<&str> = s.split(';').collect();
    check!(r#"same as str::split on a mixed string"#, ours == theirs, true);
}

#[test]
fn leading() {
    check!(r#"",a", ','"#, split_on(",a", ',').collect::<Vec<_>>(), vec!["", "a"]);
}

#[test]
fn two_delimiters() {
    check!(r#"",,", ','"#, split_on(",,", ',').collect::<Vec<_>>(), vec!["", "", ""]);
}

#[test]
fn ends_meet_on_empty() {
    let mut it = split_on(",", ',');
    check!(r#"",": next, next_back, next"#, (it.next(), it.next_back(), it.next()), (Some(""), Some(""), None));
}

#[test]
fn stays_done() {
    let mut it = split_on("a", ',');
    check!(r#""a": next, next, next_back"#, (it.next(), it.next(), it.next_back()), (Some("a"), None, None));
}

#[test]
fn unicode_delim_at_ends() {
    check!(r#""→a→", '→'"#, split_on("→a→", '→').rev().collect::<Vec<_>>(), vec!["", "a", ""]);
}

#[test]
fn unicode_pieces() {
    check!(r#""é,日本,🦀", ','"#, split_on("é,日本,🦀", ',').collect::<Vec<_>>(), vec!["é", "日本", "🦀"]);
}

#[test]
fn random_vs_std() {
    let mut rng = anneal_prelude::Rng::new(2217);
    for _ in 0..400 {
        let len = rng.below(10);
        let s = rng.string(len, "a,é→");
        let delim = *rng.pick(&[',', '→']);
        let mut ours = split_on(&s, delim);
        let mut theirs = s.split(delim);
        let mut steps = Vec::new();
        for _ in 0..8 {
            let back = rng.bool();
            steps.push(if back { "next_back" } else { "next" });
            let (a, b) = if back { (ours.next_back(), theirs.next_back()) } else { (ours.next(), theirs.next()) };
            check!(format!("s = {s:?}, delim = {delim:?}, calls = {steps:?}"), a, b);
        }
    }
}

#[test]
fn scale_200k_pieces() {
    let s = "ab,".repeat(200_000);
    let pieces: Vec<&str> = split_on(&s, ',').collect();
    check!("s = \"ab,ab,…\" (200001 pieces)", (pieces.len(), pieces[199_999], pieces[200_000]), (200_001, "ab", ""));
}

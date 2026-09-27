use solution::*;

#[test]
fn title_twice() {
    check!(r#"out = ["T (cont.)"], items = []"#, { let mut out = vec!["T (cont.)".to_string()]; let items: [&str; 0] = []; let n = render(&mut out, &items); (n, out) }, (2, vec!["T (cont.) (cont.)".to_string(), "0 items, longest: -".to_string()]));
}

#[test]
fn empty_title() {
    check!(r#"out = [""], items = ["a"]"#, { let mut out = vec!["".to_string()]; let items: [&str; 1] = ["a"]; let n = render(&mut out, &items); (n, out) }, (3, vec![" (cont.)".to_string(), "- a".to_string(), "1 items, longest: a".to_string()]));
}

#[test]
fn empty_item() {
    check!(r#"out = [], items = ["", "a"]"#, { let mut out = Vec::<String>::new(); let items: [&str; 2] = ["", "a"]; let n = render(&mut out, &items); (n, out) }, (4, vec!["untitled".to_string(), "- ".to_string(), "- a".to_string(), "2 items, longest: a".to_string()]));
}

#[test]
fn only_empty_items() {
    check!(r#"out = [], items = ["", ""]"#, { let mut out = Vec::<String>::new(); let items: [&str; 2] = ["", ""]; let n = render(&mut out, &items); (n, out) }, (4, vec!["untitled".to_string(), "- ".to_string(), "- ".to_string(), "2 items, longest: ".to_string()]));
}

#[test]
fn dash_item() {
    check!(r#"out = [], items = ["-"]"#, { let mut out = Vec::<String>::new(); let items: [&str; 1] = ["-"]; let n = render(&mut out, &items); (n, out) }, (3, vec!["untitled".to_string(), "- -".to_string(), "1 items, longest: -".to_string()]));
}

#[test]
fn unicode_items() {
    check!(r#"out = ["日誌"], items = ["東京", "abc"]"#, { let mut out = vec!["日誌".to_string()]; let items: [&str; 2] = ["東京", "abc"]; let n = render(&mut out, &items); (n, out) }, (4, vec!["日誌 (cont.)".to_string(), "- 東京".to_string(), "- abc".to_string(), "2 items, longest: 東京".to_string()]));
}

#[test]
fn later_longer() {
    check!(r#"out = [], items = ["a", "bb", "ccc"]"#, { let mut out = Vec::<String>::new(); let items: [&str; 3] = ["a", "bb", "ccc"]; let n = render(&mut out, &items); (n, out) }, (5, vec!["untitled".to_string(), "- a".to_string(), "- bb".to_string(), "- ccc".to_string(), "3 items, longest: ccc".to_string()]));
}

#[test]
fn called_twice() {
    check!(r#"render(["a"]) twice into one out"#, { let mut out = Vec::new(); render(&mut out, &["a"]); let n = render(&mut out, &["bb"]); (n, out) }, (5, ["untitled (cont.)", "- a", "1 items, longest: a", "- bb", "1 items, longest: bb"].map(String::from).to_vec()));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6207);
    for _ in 0..300 {
        let before_len = rng.below(3);
        let mut before = Vec::new();
        for _ in 0..before_len {
            let len = rng.below(3);
            before.push(rng.string(len, "Tt"));
        }
        let n = rng.below(6);
        let mut owned = Vec::new();
        for _ in 0..n {
            let len = rng.below(4);
            owned.push(rng.string(len, "ab"));
        }
        let items: Vec<&str> = owned.iter().map(|s| s.as_str()).collect();
        let mut want = before.clone();
        match want.first_mut() {
            Some(t) => t.push_str(" (cont.)"),
            None => want.push("untitled".to_string()),
        }
        let mut longest: Option<&str> = None;
        for it in &items {
            want.push(format!("- {it}"));
            if longest.map_or(true, |l| it.len() > l.len()) {
                longest = Some(it);
            }
        }
        want.push(format!("{} items, longest: {}", items.len(), longest.unwrap_or("-")));
        let mut out = before.clone();
        let got = render(&mut out, &items);
        check!(format!("out = {before:?}, items = {items:?}"), (got, out), (want.len(), want));
    }
}

#[test]
fn many_items() {
    let owned: Vec<String> = (0..100_000).map(|i| if i == 77_777 { "x".repeat(9) } else { "y".repeat(i % 8) }).collect();
    let items: Vec<&str> = owned.iter().map(|s| s.as_str()).collect();
    let mut out = Vec::new();
    let n = render(&mut out, &items);
    check!("100000 items, one of 9 bytes", (n, out[n - 1].clone()), (100_002, "100000 items, longest: xxxxxxxxx".to_string()));
}

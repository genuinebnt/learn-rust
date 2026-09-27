use solution::*;

#[test]
fn self_loop_edge() {
    let mut i = Interner::new();
    let (pairs, added) = intern_edges(&mut i, &[("a", "a")]);
    check!(r#"intern_edges([("a", "a")])"#, (pairs.clone(), added, pairs[0].0.as_ptr() == pairs[0].1.as_ptr()), (vec![("a", "a")], 1, true));
}

#[test]
fn same_pointer_as_intern() {
    let mut i = Interner::new();
    let p = i.intern("k").as_ptr();
    let q = intern_all(&mut i, &["k"])[0].as_ptr();
    check!(r#"intern("k"), then intern_all(["k"])"#, p == q, true);
}

#[test]
fn all_already_known() {
    let mut i = Interner::new();
    i.intern("a");
    i.intern("b");
    let (pairs, added) = intern_edges(&mut i, &[("b", "a")]);
    check!(r#"intern a, b; intern_edges([("b", "a")])"#, (pairs, added), (vec![("b", "a")], 0));
}

#[test]
fn empty_name() {
    let mut i = Interner::new();
    let r = intern_all(&mut i, &["", ""]);
    check!(r#"intern_all(["", ""])"#, (r.clone(), r[0].as_ptr() == r[1].as_ptr()), (vec!["", ""], true));
}

#[test]
fn unicode_names() {
    let mut i = Interner::new();
    let r = intern_all(&mut i, &["日本", "é", "日本"]);
    check!(r#"intern_all(["日本", "é", "日本"])"#, r, vec!["日本", "é", "日本"]);
}

#[test]
fn get_after_intern_all() {
    let mut i = Interner::new();
    check!(r#"intern_all(["m"]), then get("m"), get("n")"#, { intern_all(&mut i, &["m"]); (i.get("m"), i.get("n")) }, (Some("m"), None));
}

#[test]
fn edges_order_kept() {
    let mut i = Interner::new();
    let (pairs, added) = intern_edges(&mut i, &[("c", "b"), ("a", "c")]);
    check!(r#"intern_edges([("c", "b"), ("a", "c")])"#, (pairs, added), (vec![("c", "b"), ("a", "c")], 3));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6208);
    for _ in 0..300 {
        let n = rng.below(8);
        let mut owned = Vec::new();
        for _ in 0..n {
            owned.push(rng.string(1, "abc"));
        }
        let names: Vec<&str> = owned.iter().map(|s| s.as_str()).collect();
        let mut i = Interner::new();
        let got = intern_all(&mut i, &names);
        // Equal names share one stored String.
        let mut shared = true;
        for x in 0..got.len() {
            for y in 0..got.len() {
                if (got[x] == got[y]) != (got[x].as_ptr() == got[y].as_ptr()) {
                    shared = false;
                }
            }
        }
        let got: Vec<String> = got.iter().map(|s| s.to_string()).collect();
        let mut distinct = names.clone();
        distinct.sort();
        distinct.dedup();
        check!(format!("intern_all({names:?})"), (got, shared, i.len()), (owned.clone(), true, distinct.len()));
    }
}

#[test]
fn many_edges() {
    let owned: Vec<String> = (0..1000).map(|k| format!("n{k}")).collect();
    let edges: Vec<(&str, &str)> = (0..100_000).map(|k| (owned[k % 1000].as_str(), owned[(k * 7 + 3) % 1000].as_str())).collect();
    let mut i = Interner::new();
    let (pairs, added) = intern_edges(&mut i, &edges);
    check!("100000 edges over 1000 names", (pairs.len(), added, pairs[99_999]), (100_000, 1000, ("n999", "n996")));
}

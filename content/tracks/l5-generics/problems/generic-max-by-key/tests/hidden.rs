use solution::*;

#[test]
fn single() {
    check!(r#"[5], key = identity"#, max_by_key(&[5], |x| *x), Some(&5));
}

#[test]
fn negated_key_finds_min() {
    check!(r#"[3, -2, 8], key = -x"#, max_by_key(&[3, -2, 8], |x: &i32| -x), Some(&-2));
}

#[test]
fn all_ties_first() {
    let v = [1, 2, 3];
    check!(r#"[1, 2, 3], key = constant 0: which item?"#, std::ptr::eq(max_by_key(&v, |_| 0).unwrap(), &v[0]), true);
}

#[test]
fn reverse_key_first_min() {
    let v = [3, 1, 1];
    check!(r#"[3, 1, 1], key = Reverse(x): which 1?"#, std::ptr::eq(max_by_key(&v, |x| std::cmp::Reverse(*x)).unwrap(), &v[1]), true);
}

#[test]
fn tuple_key() {
    let v = [("a", 1, 30), ("b", 2, 20), ("c", 2, 25)];
    check!(r#"(dept, age) key"#, max_by_key(&v, |p| (p.1, p.2)).map(|p| p.0), Some("c"));
}

#[test]
fn calls_on_empty() {
    let v: [i32; 0] = [];
    let mut calls = 0;
    let _ = max_by_key(&v, |x| {
        calls += 1;
        *x
    });
    check!(r#"[] counts the calls"#, calls, 0);
}

#[test]
fn calls_with_many_ties() {
    let v = [7; 6];
    let mut calls = 0;
    let _ = max_by_key(&v, |x| {
        calls += 1;
        *x
    });
    check!(r#"[7; 6], count the calls"#, calls, 6);
}

#[test]
fn no_clone_items_or_keys() {
    #[derive(PartialEq, Eq, PartialOrd, Ord)]
    struct Key(i32);
    struct Item(i32);
    let v = [Item(1), Item(5), Item(-3)];
    check!(r#"items and keys that are neither Clone nor Copy"#, max_by_key(&v, |x| Key(x.0 * 2)).map(|x| x.0), Some(5));
}

#[test]
fn extremes() {
    check!(r#"[i64::MIN, i64::MAX], key = identity"#, max_by_key(&[i64::MIN, i64::MAX], |x| *x), Some(&i64::MAX));
}

#[test]
fn unicode_len() {
    check!(r#"["éé", "abc"], key = chars().count()"#, max_by_key(&["éé", "abc"], |w| w.chars().count()), Some(&"abc"));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4504);
    for _ in 0..300 {
        let n = rng.below(8);
        let words: Vec<String> = (0..n).map(|_| { let len = rng.below(4); rng.string(len, "ab") }).collect();
        let mut want: Option<usize> = None;
        for i in 0..n {
            if want.map_or(true, |w| words[i].len() > words[w].len()) {
                want = Some(i);
            }
        }
        let mut calls = 0;
        let got = max_by_key(&words, |w| {
            calls += 1;
            w.len()
        });
        check!(format!("words = {words:?}"), (got.map(|r| r as *const String), calls), (want.map(|i| &words[i] as *const String), n));
    }
}

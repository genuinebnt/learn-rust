use solution::*;

#[test]
fn single() {
    check!(r#"[42]"#, largest(&[42]), Some(&42));
}

#[test]
fn negatives() {
    check!(r#"[-3, -1, -2]"#, largest(&[-3, -1, -2]), Some(&-1));
}

#[test]
fn extremes() {
    check!(r#"[i64::MIN, i64::MAX, 0]"#, largest(&[i64::MIN, i64::MAX, 0]), Some(&i64::MAX));
}

#[test]
fn uppercase_sorts_first() {
    check!(r#"["apple", "Zebra"]"#, largest(&["apple", "Zebra"]), Some(&"apple"));
}

#[test]
fn strings() {
    let v = vec![String::from("b"), String::from("ab"), String::from("ba")];
    check!(r#"Strings ["b", "ab", "ba"]"#, largest(&v).map(String::as_str), Some("ba"));
}

#[test]
fn chars() {
    check!(r#"['q', 'z', 'a']"#, largest(&['q', 'z', 'a']), Some(&'z'));
}

#[test]
fn tuples() {
    check!(r#"[(1, 9), (2, 0), (2, -1)]"#, largest(&[(1, 9), (2, 0), (2, -1)]), Some(&(2, 0)));
}

#[test]
fn all_equal() {
    let v = [7, 7, 7];
    check!(r#"[7, 7, 7]: which 7?"#, std::ptr::eq(largest(&v).unwrap(), &v[0]), true);
}

#[test]
fn only_partial_ord() {
    #[derive(PartialEq, PartialOrd)]
    struct Weight(f64);
    let v = [Weight(1.0), Weight(2.5), Weight(-4.0)];
    check!(r#"a PartialOrd-only struct with an f64 field"#, largest(&v).map(|w| w.0), Some(2.5));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4502);
    for _ in 0..300 {
        let n = rng.below(8);
        let v: Vec<i32> = rng.vec(n, -5, 5);
        let mut want: Option<usize> = None;
        for i in 0..v.len() {
            if want.map_or(true, |w| v[i] > v[w]) {
                want = Some(i);
            }
        }
        check!(format!("items = {v:?}"), largest(&v).map(|r| r as *const i32), want.map(|i| &v[i] as *const i32));
    }
}

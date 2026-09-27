use solution::*;

#[test]
fn first_corrupt_none() {
    check!(r#"store = {a: "1", b: "x"}, first_corrupt(["a", "c"])"#, first_corrupt(&Store::new(&[("a", "1"), ("b", "x")]), &["a", "c"]), None);
}

#[test]
fn first_corrupt_first_wins() {
    check!(r#"store = {a: "x", b: "y"}, first_corrupt(["c", "b", "a"])"#, first_corrupt(&Store::new(&[("a", "x"), ("b", "y")]), &["c", "b", "a"]), Some(StoreError::Corrupt("b".to_string())));
}

#[test]
fn first_corrupt_no_keys() {
    check!(r#"store = {a: "x"}, first_corrupt([])"#, first_corrupt(&Store::new(&[("a", "x")]), &[]), None);
}

#[test]
fn sum_no_keys() {
    check!(r#"store = {a: "x"}, sum_or_zero([])"#, sum_or_zero(&Store::new(&[("a", "x")]), &[]), Ok(0));
}

#[test]
fn sum_all_missing() {
    check!(r#"store = {}, sum_or_zero(["a", "b"])"#, sum_or_zero(&Store::new(&[]), &["a", "b"]), Ok(0));
}

#[test]
fn sum_repeated_key() {
    check!(r#"store = {a: "5"}, sum_or_zero(["a", "a"])"#, sum_or_zero(&Store::new(&[("a", "5")]), &["a", "a"]), Ok(10));
}

#[test]
fn sum_first_corrupt_wins() {
    check!(r#"store = {a: "x", b: "y"}, sum_or_zero(["c", "b", "a"])"#, sum_or_zero(&Store::new(&[("a", "x"), ("b", "y")]), &["c", "b", "a"]), Err(StoreError::Corrupt("b".to_string())));
}

#[test]
fn sum_corrupt_key_not_asked() {
    check!(r#"store = {a: "2", b: "x"}, sum_or_zero(["a"])"#, sum_or_zero(&Store::new(&[("a", "2"), ("b", "x")]), &["a"]), Ok(2));
}

#[test]
fn require_empty_value() {
    check!(r#"store = {a: ""}, require("a")"#, require(&Store::new(&[("a", "")]), "a"), Err(StoreError::Corrupt("a".to_string())));
}

#[test]
fn require_zero_is_present() {
    check!(r#"store = {a: "0"}, require("a")"#, require(&Store::new(&[("a", "0")]), "a"), Ok(0));
}

#[test]
fn require_i64_bounds() {
    let s = Store::new(&[("lo", "-9223372036854775808"), ("hi", "9223372036854775807")]);
    check!(r#"store = {lo: "-9223372036854775808", hi: "9223372036854775807"}"#, (require(&s, "lo"), require(&s, "hi")), (Ok(i64::MIN), Ok(i64::MAX)));
}

#[test]
fn require_empty_key() {
    check!(r#"store = {a: "1"}, require("")"#, require(&Store::new(&[("a", "1")]), ""), Err(StoreError::Missing(String::new())));
}

#[test]
fn require_unicode_key() {
    let s = Store::new(&[("ключ", "7")]);
    check!(r#"store = {ключ: "7"}, require("ключ"), require("клю")"#, (require(&s, "ключ"), require(&s, "клю")), (Ok(7), Err(StoreError::Missing("клю".to_string()))));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1313);
    let names = ["a", "b", "c", "d"];
    let values = ["1", "-3", "10", "x", "", "7"];
    for _ in 0..400 {
        let mut pairs: Vec<(&str, &str)> = Vec::new();
        for &k in &names {
            if rng.bool() {
                pairs.push((k, *rng.pick(&values)));
            }
        }
        let store = Store::new(&pairs);
        let n = rng.below(5);
        let mut keys: Vec<&str> = Vec::new();
        for _ in 0..n {
            keys.push(*rng.pick(&names));
        }
        let lookup = |k: &str| pairs.iter().find(|(pk, _)| *pk == k).map(|(_, v)| *v);
        let key = *rng.pick(&names);
        let want_one = match lookup(key) {
            None => Err(StoreError::Missing(key.to_string())),
            Some(v) => v.parse::<i64>().map_err(|_| StoreError::Corrupt(key.to_string())),
        };
        check!(format!("store = {pairs:?}, require({key:?})"), require(&store, key), want_one);
        let mut want: Result<i64, StoreError> = Ok(0);
        for &k in &keys {
            match lookup(k).map(|v| v.parse::<i64>()) {
                None => {}
                Some(Ok(v)) => {
                    if let Ok(t) = &mut want {
                        *t += v;
                    }
                }
                Some(Err(_)) => {
                    want = Err(StoreError::Corrupt(k.to_string()));
                    break;
                }
            }
        }
        check!(format!("store = {pairs:?}, sum_or_zero({keys:?})"), sum_or_zero(&store, &keys), want);
        let want_first = keys.iter().find(|&&k| lookup(k).is_some_and(|v| v.parse::<i64>().is_err())).map(|k| StoreError::Corrupt(k.to_string()));
        check!(format!("store = {pairs:?}, first_corrupt({keys:?})"), first_corrupt(&store, &keys), want_first);
    }
}

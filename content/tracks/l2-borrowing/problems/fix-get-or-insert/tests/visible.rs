use solution::*;

#[test]
fn hit_and_miss() {
    let mut c = Cache::new();
    check!(r#"get_or_make 1 ("one"), then 1 again ("uno")"#, (c.get_or_make(1, || "one".to_string()).clone(), c.get_or_make(1, || "uno".to_string()).clone(), c.misses()), ("one".to_string(), "one".to_string(), 1));
}

#[test]
fn make_runs_only_on_a_miss() {
    let mut c = Cache::new();
    let mut calls = 0;
    c.get_or_make(5, || { calls += 1; "x".to_string() });
    c.get_or_make(5, || { calls += 1; "y".to_string() });
    check!(r#"get_or_make 5 twice, counting calls to make"#, calls, 1);
}

#[test]
fn edit_in_place() {
    let mut c = Cache::new();
    c.get_or_make_mut(2, || "a".to_string()).push('b');
    c.get_or_make_mut(2, || "z".to_string()).push('c');
    check!(r#"get_or_make_mut 2 ("a") += "b", then += "c""#, c.get_or_make(2, String::new).clone(), "abc".to_string());
}

#[test]
fn order_of_first_store() {
    let mut c = Cache::new();
    for k in [3, 1, 3, 2, 1] {
        c.get_or_make(k, || k.to_string());
    }
    check!(r#"keys 3, 1, 3, 2, 1"#, (c.order().to_vec(), c.misses()), (vec![3, 1, 2], 3));
}

#[test]
fn empty_value() {
    let mut c = Cache::new();
    check!(r#"get_or_make 0 ("")"#, c.get_or_make(0, String::new).len(), 0);
}

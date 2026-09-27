use solution::*;

#[test]
fn owned_vec_of_strings() {
    check!(r#"vec!["héllo", "ab"] as Strings"#, total_chars(vec!["héllo".to_string(), "ab".to_string()]), 7);
}

#[test]
fn join_a_range() {
    check!(r#"1..=3, ", ""#, join_display(1..=3, ", "), "1, 2, 3");
}

#[test]
fn closure_captures() {
    let min = 3;
    let words = vec!["tree".to_string(), "sky".to_string(), "forest".to_string()];
    check!(r#"words longer than min = 3"#, count_where(&words, |w| w.len() > min), 2);
}

#[test]
fn compose_closures() {
    let k = 3;
    let h = compose(move |x| x + k, |x| x * 2);
    check!(r#"compose(x + k, x * 2)(1) with k = 3"#, h(1), 8);
}

#[test]
fn evens_is_lazy_and_clone() {
    let e = evens(u64::MAX).take(3);
    check!(r#"evens(u64::MAX).take(3), cloned"#, (e.clone().collect::<Vec<_>>(), e.count()), (vec![0, 2, 4], 3));
}

#[test]
fn ordered_both_ways() {
    let v = [1, 2, 3];
    check!(r#"ordered(&[1, 2, 3], true / false)"#, (ordered(&v, true).copied().collect::<Vec<_>>(), ordered(&v, false).copied().collect::<Vec<_>>()), (vec![3, 2, 1], vec![1, 2, 3]));
}

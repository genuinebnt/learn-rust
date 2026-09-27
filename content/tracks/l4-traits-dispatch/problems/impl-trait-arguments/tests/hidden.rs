use solution::*;

#[test]
fn array_of_str() {
    check!(r#"["a", "bc"]"#, total_chars(["a", "bc"]), 3);
}

#[test]
fn split_iterator() {
    check!(r#""one two".split(' ')"#, total_chars("one two".split(' ')), 6);
}

#[test]
fn empty_iter() {
    check!(r#"std::iter::empty::<&str>()"#, total_chars(std::iter::empty::<&str>()), 0);
}

#[test]
fn borrowed_vec_still_usable() {
    let v = vec!["abc".to_string(), "de".to_string()];
    check!(r#"&v, then v.len()"#, (total_chars(&v), v.len()), (5, 2));
}

#[test]
fn join_floats_by_ref() {
    check!(r#"&[1.5, 2.0], "|""#, join_display(&[1.5, 2.0], "|"), "1.5|2");
}

#[test]
fn join_empty() {
    check!(r#"Vec::<i32>::new()"#, join_display(Vec::<i32>::new(), ","), String::new());
}

#[test]
fn fn_item_still_works() {
    check!(r#"["", "a"], str::is_empty"#, count_where(["", "a"], str::is_empty), 1);
}

#[test]
fn compose_order() {
    check!(r#"compose(x * 10, x + 1)(2)"#, compose(|x| x * 10, |x| x + 1)(2), 21);
}

#[test]
fn compose_nested() {
    check!(r#"compose(compose(+1, *2), -3)(5)"#, compose(compose(|x| x + 1, |x| x * 2), |x| x - 3)(5), 9);
}

#[test]
fn evens_inclusive() {
    check!(r#"evens(6)"#, evens(6).collect::<Vec<_>>(), vec![0, 2, 4, 6]);
}

#[test]
fn evens_zero() {
    check!(r#"evens(0)"#, evens(0).collect::<Vec<_>>(), vec![0]);
}

#[test]
fn ordered_empty() {
    check!(r#"ordered(&[], true)"#, ordered(&[], true).count(), 0);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4405);
    for _ in 0..300 {
        let n = rng.below(5);
        let words: Vec<String> = (0..n).map(|_| { let len = rng.below(4); rng.string(len, "aé") }).collect();
        let chars: usize = words.iter().map(|w| w.chars().count()).sum();
        check!(format!("total_chars({words:?})"), total_chars(&words), chars);
        check!(format!("join_display({words:?}, \"/\")"), join_display(&words, "/"), words.join("/"));
        let limit = rng.below(20) as u64;
        check!(format!("evens({limit})"), evens(limit).collect::<Vec<_>>(), (0..=limit).filter(|x| x % 2 == 0).collect::<Vec<_>>());
        let v: Vec<i32> = rng.vec(n, -9, 9);
        let desc = rng.bool();
        let mut want = v.clone();
        if desc {
            want.reverse();
        }
        check!(format!("ordered({v:?}, {desc})"), ordered(&v, desc).copied().collect::<Vec<_>>(), want);
    }
}

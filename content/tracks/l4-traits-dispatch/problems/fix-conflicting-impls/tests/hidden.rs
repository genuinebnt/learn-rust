use solution::*;

#[test]
fn empty_vec() {
    check!(r#"Vec::<i32>::new()"#, Vec::<i32>::new().label(), "[]");
}

#[test]
fn none_alone() {
    check!(r#"None::<String>"#, None::<String>.label(), "-");
}

#[test]
fn option_of_vec() {
    check!(r#"Some(vec![1u64, 2])"#, Some(vec![1u64, 2]).label(), "[1, 2]");
}

#[test]
fn float_whole() {
    check!(r#"1.0"#, 1.0f64.label(), "1");
}

#[test]
fn i64_min() {
    check!(r#"i64::MIN"#, i64::MIN.label(), "-9223372036854775808");
}

#[test]
fn vec_of_strings() {
    check!(r#"vec![String "x y", String ""]"#, vec![String::from("x y"), String::new()].label(), "[x y, ]");
}

#[test]
fn deep_nesting() {
    check!(r#"vec![vec![Some(vec!['a'])], vec![None]]"#, vec![vec![Some(vec!['a'])], vec![None]].label(), "[[[a]], [-]]");
}

#[test]
fn unicode_char_and_str() {
    check!(r#"vec!['é'], "日本""#, (vec!['é'].label(), "日本".label()), ("[é]".to_string(), "日本".to_string()));
}

#[test]
fn borrowed_vec() {
    check!(r#"&vec![true, false]"#, (&vec![true, false]).label(), "[true, false]");
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4418);
    for _ in 0..300 {
        let n = rng.below(4);
        let v: Vec<Option<i32>> = (0..n).map(|_| if rng.bool() { Some(rng.int(-20, 20) as i32) } else { None }).collect();
        let want = format!("[{}]", v.iter().map(|x| x.map_or("-".to_string(), |x| x.to_string())).collect::<Vec<_>>().join(", "));
        check!(format!("{v:?}"), v.label(), want);
    }
}

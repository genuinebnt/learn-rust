use solution::*;

#[test]
fn strings() {
    check!(r#"Pair::new(String::from("x"), String::from("y"))"#, Pair::new(String::from("x"), String::from("y")).to_string(), "(x, y)");
}

#[test]
fn floats() {
    check!(r#"Pair::new(1.5, -0.25)"#, Pair::new(1.5, -0.25).to_string(), "(1.5, -0.25)");
}

#[test]
fn chars() {
    check!(r#"Pair::new('a', 'é')"#, Pair::new('a', 'é').to_string(), "(a, é)");
}

#[test]
fn empty_strs() {
    check!(r#"Pair::new("", "")"#, Pair::new("", "").to_string(), "(, )");
}

#[test]
fn swap_then_print() {
    check!(r#"Pair::new(1, 2).swap()"#, Pair::new(1, 2).swap().to_string(), "(2, 1)");
}

#[test]
fn in_format() {
    check!(r#"format!("p = {}", Pair::new(3, 4))"#, format!("p = {}", Pair::new(3, 4)), "p = (3, 4)");
}

#[test]
fn new_without_display() {
    check!(r#"Pair::new(vec![1], vec![2]) (Vec isn't Display)"#, Pair::new(vec![1], vec![2]).first, vec![1]);
}

#[test]
fn swap_twice() {
    #[derive(Debug, PartialEq)]
    struct Opaque(u8);
    check!(r#"Pair::new(Opaque(1), Opaque(2)).swap().swap()"#, Pair::new(Opaque(1), Opaque(2)).swap().swap(), Pair { first: Opaque(1), second: Opaque(2) });
}

#[test]
fn unicode_strings() {
    check!(r#"Pair::new("héllo", "wörld")"#, Pair::new("héllo", "wörld").to_string(), "(héllo, wörld)");
}

#[test]
fn random_vs_format() {
    let mut rng = anneal_prelude::Rng::new(4503);
    for _ in 0..200 {
        let (a, b) = (rng.int(-1000, 1000), rng.int(-1000, 1000));
        check!(format!("Pair::new({a}, {b})"), Pair::new(a, b).to_string(), format!("({a}, {b})"));
        check!(format!("Pair::new({a}, {b}).swap()"), Pair::new(a, b).swap(), Pair { first: b, second: a });
    }
}

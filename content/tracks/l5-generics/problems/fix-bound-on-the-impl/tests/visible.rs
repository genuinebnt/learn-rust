use solution::*;

#[test]
fn integers() {
    check!(r#"Pair::new(1, 2)"#, Pair::new(1, 2).to_string(), "(1, 2)");
}

#[test]
fn strs() {
    check!(r#"Pair::new("a", "b")"#, Pair::new("a", "b").to_string(), "(a, b)");
}

#[test]
fn swap() {
    check!(r#"Pair::new(1, 2).swap()"#, Pair::new(1, 2).swap(), Pair { first: 2, second: 1 });
}

#[test]
fn swap_works_without_display() {
    #[derive(Debug, PartialEq)]
    struct Opaque(u8);
    check!(r#"a type that isn't Display: Pair::new(Opaque(1), Opaque(2)).swap()"#, Pair::new(Opaque(1), Opaque(2)).swap(), Pair { first: Opaque(2), second: Opaque(1) });
}

#[test]
fn nested() {
    check!(r#"Pair::new(Pair::new(1, 2), Pair::new(3, 4))"#, Pair::new(Pair::new(1, 2), Pair::new(3, 4)).to_string(), "((1, 2), (3, 4))");
}

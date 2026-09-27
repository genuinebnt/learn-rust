use solution::*;

#[test]
fn sum_all_three() {
    check!(r#"sum_all([1 + 2x, 3, x²])"#, sum_all(&[Poly(vec![1, 2]), Poly(vec![3]), Poly(vec![0, 0, 1])]), Poly(vec![4, 2, 1]));
}

#[test]
fn owned_plus_ref() {
    check!(r#"Poly [1, 2] + &Poly [0, 0, 5]"#, Poly(vec![1, 2]) + &Poly(vec![0, 0, 5]), Poly(vec![1, 2, 5]));
}

#[test]
fn ref_plus_ref_keeps_both() {
    let a = Poly(vec![1, 2]);
    let b = Poly(vec![2, 1]);
    check!(r#"&a + &b, then a and b"#, (&a + &b, a, b), (Poly(vec![3, 3]), Poly(vec![1, 2]), Poly(vec![2, 1])));
}

#[test]
fn add_assign_ref() {
    let mut p = Poly(vec![5]);
    p += &Poly(vec![1, 1]);
    check!(r#"p = [5]; p += &[1, 1]"#, p, Poly(vec![6, 1]));
}

#[test]
fn cancelling_trims() {
    check!(r#"[1, 2] + &[0, -2]"#, Poly(vec![1, 2]) + &Poly(vec![0, -2]), Poly(vec![1]));
}

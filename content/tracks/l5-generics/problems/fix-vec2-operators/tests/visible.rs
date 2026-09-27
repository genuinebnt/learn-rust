use solution::*;

/// A number that is not Copy or Clone.
#[derive(Debug, PartialEq, Default)]
struct Big(i128);

impl std::ops::Add for Big {
    type Output = Big;
    fn add(self, o: Big) -> Big {
        Big(self.0 + o.0)
    }
}

impl std::ops::Sub for Big {
    type Output = Big;
    fn sub(self, o: Big) -> Big {
        Big(self.0 - o.0)
    }
}

impl std::ops::Neg for Big {
    type Output = Big;
    fn neg(self) -> Big {
        Big(-self.0)
    }
}

impl std::ops::AddAssign for Big {
    fn add_assign(&mut self, o: Big) {
        self.0 += o.0;
    }
}

impl std::ops::Mul for Big {
    type Output = Big;
    fn mul(self, o: Big) -> Big {
        Big(self.0 * o.0)
    }
}

/// Works for any type whose dot product is with itself: needs `Dot`'s default type parameter.
fn len_sq<V: Dot + Copy>(v: V) -> V::Output {
    v.dot(v)
}

#[test]
fn add() {
    check!(r#"(1, 2) + (3, 4)"#, Vec2::new(1, 2) + Vec2::new(3, 4), Vec2::new(4, 6));
}

#[test]
fn scale() {
    check!(r#"(1.5, -2.0) * 2.0"#, Vec2::new(1.5, -2.0) * 2.0, Vec2::new(3.0, -4.0));
}

#[test]
fn neg_and_sub() {
    check!(r#"-(1, 2) - (3, 4)"#, -Vec2::new(1, 2) - Vec2::new(3, 4), Vec2::new(-4, -6));
}

#[test]
fn sum() {
    check!(r#"[(1, 1), (2, 3), (-1, 0)].sum()"#, vec![Vec2::new(1, 1), Vec2::new(2, 3), Vec2::new(-1, 0)].into_iter().sum::<Vec2<i32>>(), Vec2::new(2, 4));
}

#[test]
fn dot_with_default_rhs() {
    check!(r#"len_sq((3, 4)), where len_sq takes V: Dot"#, len_sq(Vec2::new(3, 4)), 25);
}

#[test]
fn no_copy_needed() {
    let mut v = Vec2::new(Big(1), Big(2)) + Vec2::new(Big(3), Big(4)) - Vec2::new(Big(0), Big(1));
    v += Vec2::new(Big(2), Big(4));
    check!(r#"Big values: (a + b - c), then += and neg"#, -v, Vec2::new(Big(-6), Big(-9)));
}

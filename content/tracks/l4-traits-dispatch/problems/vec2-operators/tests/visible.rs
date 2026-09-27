use solution::*;

#[test]
fn add_sub_neg() {
    let (a, b) = (Vec2 { x: 1, y: 2 }, Vec2 { x: 10, y: 20 });
    check!(r#"a = (1, 2), b = (10, 20): a + b, b - a, -a"#, (a + b, b - a, -a), (Vec2 { x: 11, y: 22 }, Vec2 { x: 9, y: 18 }, Vec2 { x: -1, y: -2 }));
}

#[test]
fn scale_both_sides() {
    let v = Vec2 { x: 2, y: -3 };
    check!(r#"v = (2, -3): v * 3, 3 * v"#, (v * 3, 3 * v), (Vec2 { x: 6, y: -9 }, Vec2 { x: 6, y: -9 }));
}

#[test]
fn dot_product() {
    check!(r#"(1, 2) * (3, 4)"#, Vec2 { x: 1, y: 2 } * Vec2 { x: 3, y: 4 }, 11);
}

#[test]
fn walk_steps() {
    check!(r#"walk [((1, 0), 3), ((0, 1), 2)]"#, walk(&[(Vec2 { x: 1, y: 0 }, 3), (Vec2 { x: 0, y: 1 }, 2)]), Vec2 { x: 3, y: 2 });
}

#[test]
fn sum_owned_and_borrowed() {
    let v = vec![Vec2 { x: 1, y: 1 }, Vec2 { x: 2, y: 3 }];
    check!(r#"sum of [(1, 1), (2, 3)], owned and by reference"#, (v.iter().sum::<Vec2>(), v.into_iter().sum::<Vec2>()), (Vec2 { x: 3, y: 4 }, Vec2 { x: 3, y: 4 }));
}

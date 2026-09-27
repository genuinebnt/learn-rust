use solution::*;

#[test]
fn circle_perimeter() {
    check!(r#"Circle { r: 2.5 }.perimeter(), 4 decimals"#, format!("{:.4}", Circle { r: 2.5 }.perimeter()), "15.7080");
}

#[test]
fn rect_perimeter() {
    check!(r#"Rect { w: 2.0, h: 3.5 }.perimeter()"#, Rect { w: 2.0, h: 3.5 }.perimeter(), 11.0);
}

#[test]
fn describe_rounds() {
    check!(r#"Circle { r: 2.0 }.describe()"#, Circle { r: 2.0 }.describe(), "circle, 0 sides, area 12.57");
}

#[test]
fn describe_zero_rect() {
    check!(r#"Rect { w: 0.0, h: 9.0 }.describe()"#, Rect { w: 0.0, h: 9.0 }.describe(), "rect, 4 sides, area 0.00");
}

#[test]
fn total_sides_empty() {
    check!(r#"total_sides::<Rect>(&[])"#, total_sides::<Rect>(&[]), 0);
}

#[test]
fn total_sides_rects() {
    check!(r#"three rects"#, total_sides(&[Rect { w: 1.0, h: 1.0 }, Rect { w: 2.0, h: 1.0 }, Rect { w: 3.0, h: 1.0 }]), 12);
}

#[test]
fn total_sides_circles() {
    check!(r#"two circles"#, total_sides(&[Circle { r: 1.0 }, Circle { r: 2.0 }]), 0);
}

#[test]
fn label_untouched() {
    check!(r#"<Rect as Label>::name"#, <Rect as Label>::name(&Rect { w: 1.0, h: 1.0 }), "box");
}

#[test]
fn named_on_circle() {
    check!(r#"Named::name(&Circle { r: 1.0 })"#, Named::name(&Circle { r: 1.0 }), "circle");
}

#[test]
fn supertrait_gives_name() {
    // With only `S: Shape` in scope, `name` must come from the supertrait.
    fn via_shape<S: Shape>(s: &S) -> String {
        s.name()
    }
    check!("via_shape(&Rect { w: 1.0, h: 1.0 })", via_shape(&Rect { w: 1.0, h: 1.0 }), "rect");
    check!("via_shape(&Circle { r: 1.0 })", via_shape(&Circle { r: 1.0 }), "circle");
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4401);
    for _ in 0..300 {
        let (w, h) = (rng.int(0, 40) as f64 / 4.0, rng.int(0, 40) as f64 / 4.0);
        let r = Rect { w, h };
        check!(format!("Rect {{ w: {w}, h: {h} }}.describe()"), r.describe(), format!("rect, 4 sides, area {:.2}", w * h));
        check!(format!("Rect {{ w: {w}, h: {h} }}.perimeter()"), r.perimeter(), 2.0 * (w + h));
        let rad = rng.int(0, 40) as f64 / 8.0;
        check!(format!("Circle {{ r: {rad} }}.describe()"), Circle { r: rad }.describe(), format!("circle, 0 sides, area {:.2}", std::f64::consts::PI * rad * rad));
    }
}

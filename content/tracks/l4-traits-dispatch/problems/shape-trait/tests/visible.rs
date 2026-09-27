use solution::*;

#[test]
fn describe_circle() {
    check!(r#"Circle { r: 1.0 }.describe()"#, Circle { r: 1.0 }.describe(), "circle, 0 sides, area 3.14");
}

#[test]
fn describe_uses_named() {
    check!(r#"Rect { w: 2.0, h: 3.0 }.describe()"#, Rect { w: 2.0, h: 3.0 }.describe(), "rect, 4 sides, area 6.00");
}

#[test]
fn sides_const() {
    check!(r#"<Rect as Shape>::SIDES, Circle::SIDES"#, (<Rect as Shape>::SIDES, Circle::SIDES), (4, 0));
}

#[test]
fn both_names_rect() {
    check!(r#"both_names(&Rect { w: 1.0, h: 1.0 })"#, both_names(&Rect { w: 1.0, h: 1.0 }), "rect/box");
}

#[test]
fn a_new_shape() {
    // Implemented outside your crate: it only needs Named, the const, area and perimeter.
    struct Tri(f64);
    impl Named for Tri {
        fn name(&self) -> String {
            "tri".to_string()
        }
    }
    impl Shape for Tri {
        const SIDES: u32 = 3;
        fn area(&self) -> f64 {
            self.0 * self.0 * 3f64.sqrt() / 4.0
        }
        fn perimeter(&self) -> f64 {
            3.0 * self.0
        }
    }
    check!("Tri(2.0).describe()", Tri(2.0).describe(), "tri, 3 sides, area 1.73");
    check!("total_sides(&[Tri(1.0), Tri(2.0)])", total_sides(&[Tri(1.0), Tri(2.0)]), 6);
}

use solution::*;

#[test]
fn generic_on_one_type() {
    check!(r#"total_area_generic(&[Circle 1, Circle 2])"#, format!("{:.4}", total_area_generic(&[Circle { radius: 1.0 }, Circle { radius: 2.0 }])), "15.7080");
}

#[test]
fn generic_on_boxes() {
    let boxes: Vec<Box<dyn Shape>> = vec![Box::new(Circle { radius: 1.0 }), Box::new(Rectangle { width: 2.0, height: 3.0 })];
    check!(r#"total_area_generic(&[Box Circle 1, Box Rect 2x3])"#, format!("{:.4}", total_area_generic(&boxes)), "9.1416");
}

#[test]
fn dyn_on_refs() {
    let a = Rectangle { width: 1.0, height: 1.0 };
    let b = Rectangle { width: 2.0, height: 2.0 };
    check!(r#"total_area_dyn(&[&Rect 1x1, &Rect 2x2])"#, total_area_dyn(&[&a, &b]), 5.0);
}

#[test]
fn largest_tie_is_first() {
    check!(r#"largest(&[Rect 2x3, Rect 3x2])"#, largest(&[Rectangle { width: 2.0, height: 3.0 }, Rectangle { width: 3.0, height: 2.0 }]).map(|s| s.name()), Some("rect(2x3)".to_string()));
}

#[test]
fn largest_boxed() {
    let boxes: Vec<Box<dyn Shape>> = vec![Box::new(Circle { radius: 1.0 }), Box::new(Rectangle { width: 1.0, height: 4.0 })];
    check!(r#"largest(&[Box Circle 1, Box Rect 1x4])"#, largest(&boxes).map(|s| s.name()), Some("rect(1x4)".to_string()));
}

#[test]
fn largest_empty() {
    check!(r#"largest::<Circle>(&[])"#, largest::<Circle>(&[]).is_none(), true);
}

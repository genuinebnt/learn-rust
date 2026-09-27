use solution::*;

#[test]
fn generic_on_dyn_refs() {
    let (a, b) = (Rectangle { width: 1.0, height: 2.0 }, Rectangle { width: 3.0, height: 1.0 });
    let refs: Vec<&dyn Shape> = vec![&a, &b];
    check!(r#"total_area_generic(&[&dyn Rect 1x2, &dyn Rect 3x1])"#, total_area_generic(&refs), 5.0);
}

#[test]
fn generic_on_plain_refs() {
    let r = Rectangle { width: 2.0, height: 2.0 };
    check!(r#"total_area_generic(&[&Rect 2x2])"#, total_area_generic(&[&r]), 4.0);
}

#[test]
fn box_of_box() {
    check!(r#"total_area_generic(&[Box<Box<Rect 3x3>>])"#, total_area_generic(&[Box::new(Box::new(Rectangle { width: 3.0, height: 3.0 }))]), 9.0);
}

#[test]
fn largest_dyn_tie() {
    let (a, b, c) = (Rectangle { width: 1.0, height: 6.0 }, Rectangle { width: 6.0, height: 1.0 }, Rectangle { width: 2.0, height: 3.0 });
    let refs: Vec<&dyn Shape> = vec![&a, &b, &c];
    check!(r#"largest(&[&dyn Rect 1x6, &dyn Rect 6x1, &dyn Rect 2x3])"#, largest(&refs).map(|s| s.name()), Some("rect(1x6)".to_string()));
}

#[test]
fn largest_tie_in_the_middle() {
    let v = [Rectangle { width: 1.0, height: 1.0 }, Rectangle { width: 2.0, height: 2.0 }, Rectangle { width: 4.0, height: 1.0 }, Rectangle { width: 2.0, height: 1.0 }];
    check!(r#"areas [1, 4, 4, 2]"#, largest(&v).map(|s| s.name()), Some("rect(2x2)".to_string()));
}

#[test]
fn largest_all_zero() {
    check!(r#"areas [0, 0]"#, largest(&[Rectangle { width: 0.0, height: 1.0 }, Rectangle { width: 1.0, height: 0.0 }]).map(|s| s.name()), Some("rect(0x1)".to_string()));
}

#[test]
fn largest_returns_the_element() {
    let v = [Circle { radius: 1.0 }, Circle { radius: 3.0 }, Circle { radius: 2.0 }];
    check!(r#"largest points into the slice"#, std::ptr::eq(largest(&v).unwrap(), &v[1]), true);
}

#[test]
fn name_through_box() {
    let b: Box<dyn Shape> = Box::new(Circle { radius: 2.5 });
    check!(r#"Box<dyn Shape>::name"#, b.name(), "circle(2.5)");
}

#[test]
fn empty_totals() {
    check!(r#"total_area_generic::<Box<dyn Shape>>(&[]), total_area_dyn(&[])"#, (total_area_generic::<Box<dyn Shape>>(&[]), total_area_dyn(&[])), (0.0, 0.0));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4406);
    for _ in 0..300 {
        let n = rng.below(6);
        let dims: Vec<(f64, f64)> = (0..n).map(|_| (rng.int(0, 3) as f64, rng.int(0, 3) as f64)).collect();
        let boxes: Vec<Box<dyn Shape>> = dims.iter().map(|&(w, h)| Box::new(Rectangle { width: w, height: h }) as Box<dyn Shape>).collect();
        let mut best: Option<usize> = None;
        for (i, &(w, h)) in dims.iter().enumerate() {
            if best.map_or(true, |b| w * h > dims[b].0 * dims[b].1) {
                best = Some(i);
            }
        }
        let want = best.map(|i| format!("rect({}x{})", dims[i].0, dims[i].1));
        check!(format!("largest({dims:?})"), largest(&boxes).map(|s| s.name()), want);
        check!(format!("total({dims:?})"), total_area_generic(&boxes), dims.iter().map(|&(w, h)| w * h).sum::<f64>());
    }
}

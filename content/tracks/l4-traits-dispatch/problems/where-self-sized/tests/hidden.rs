use solution::*;

#[test]
fn box_clone_is_a_new_allocation() {
    let b: Box<dyn Shape> = Box::new(Circle { r: 1.0 });
    let c = b.clone();
    check!(r#"b.clone() vs b"#, std::ptr::addr_eq(b.as_ref(), c.as_ref()), false);
}

#[test]
fn scaled_box_on_dyn() {
    let b: Box<dyn Shape> = Box::new(Rect { w: 2.0, h: 2.0 });
    check!(r#"Box<dyn Shape> Rect 2x2 .scaled_box(1.5)"#, b.scaled_box(1.5).area(), 9.0);
}

#[test]
fn scale_by_zero() {
    let scene: Vec<Box<dyn Shape>> = vec![Box::new(Rect { w: 3.0, h: 4.0 })];
    check!(r#"scale_all([Rect 3x4], 0)"#, scale_all(&scene, 0.0)[0].area(), 0.0);
}

#[test]
fn scale_leaves_input() {
    let scene: Vec<Box<dyn Shape>> = vec![Box::new(Circle { r: 2.0 })];
    check!(r#"scale_all then read the input"#, (scale_all(&scene, 3.0)[0].name(), scene[0].name()), ("circle(6)".to_string(), "circle(2)".to_string()));
}

#[test]
fn empty_scene() {
    check!(r#"snapshot(&vec![]), scale_all(&[], 2)"#, (snapshot(&vec![]).len(), scale_all(&[], 2.0).len()), (0, 0));
}

#[test]
fn rect_scaled() {
    check!(r#"Rect { w: 1, h: 4 }.scaled(0.5)"#, Rect { w: 1.0, h: 4.0 }.scaled(0.5), Rect { w: 0.5, h: 2.0 });
}

#[test]
fn clone_of_clone() {
    let b: Box<dyn Shape> = Box::new(Circle { r: 7.0 });
    check!(r#"b.clone().clone()"#, b.clone().clone().name(), "circle(7)");
}

#[test]
fn circle_area_scales_by_k_squared() {
    check!(r#"Circle 1 scaled_box(3)"#, format!("{:.4}", Circle { r: 1.0 }.scaled_box(3.0).area()), "28.2743");
}

#[test]
fn snapshot_many() {
    let scene: Vec<Box<dyn Shape>> = vec![Box::new(Circle { r: 1.0 }), Box::new(Rect { w: 2.0, h: 2.0 }), Box::new(Circle { r: 3.0 })];
    check!(r#"snapshot of 3 shapes"#, snapshot(&scene).iter().map(|s| s.name()).collect::<Vec<_>>(), vec!["circle(1)", "rect(2x2)", "circle(3)"]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4413);
    for _ in 0..200 {
        let n = rng.below(5);
        let dims: Vec<(f64, f64)> = (0..n).map(|_| (rng.int(1, 4) as f64, rng.int(1, 4) as f64)).collect();
        let scene: Vec<Box<dyn Shape>> = dims.iter().map(|&(w, h)| Box::new(Rect { w, h }) as Box<dyn Shape>).collect();
        let k = rng.int(0, 4) as f64 / 2.0;
        let got: Vec<f64> = scale_all(&scene, k).iter().map(|s| s.area()).collect();
        let want: Vec<f64> = dims.iter().map(|&(w, h)| w * k * h * k).collect();
        check!(format!("scale_all({dims:?}, {k})"), got, want);
    }
}

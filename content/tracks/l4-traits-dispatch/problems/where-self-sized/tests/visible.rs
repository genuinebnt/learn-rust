use solution::*;

#[test]
fn snapshot_is_independent() {
    let mut scene: Vec<Box<dyn Shape>> = vec![Box::new(Circle { r: 1.0 })];
    let snap = snapshot(&scene);
    scene[0] = Box::new(Rect { w: 1.0, h: 1.0 });
    check!(r#"snapshot, then replace scene[0]"#, (snap[0].name(), scene[0].name()), ("circle(1)".to_string(), "rect(1x1)".to_string()));
}

#[test]
fn scale_all_names() {
    let scene: Vec<Box<dyn Shape>> = vec![Box::new(Circle { r: 1.0 }), Box::new(Rect { w: 2.0, h: 3.0 })];
    check!(r#"scale_all([Circle 1, Rect 2x3], 2)"#, scale_all(&scene, 2.0).iter().map(|s| s.name()).collect::<Vec<_>>(), vec!["circle(2)", "rect(4x6)"]);
}

#[test]
fn scaled_stays_concrete() {
    check!(r#"Circle { r: 1.5 }.scaled(2.0)"#, Circle { r: 1.5 }.scaled(2.0), Circle { r: 3.0 });
}

#[test]
fn vec_clone() {
    let scene: Vec<Box<dyn Shape>> = vec![Box::new(Rect { w: 1.0, h: 2.0 })];
    check!(r#"scene.clone() keeps names"#, scene.clone().iter().map(|s| s.name()).collect::<Vec<_>>(), vec!["rect(1x2)"]);
}

#[test]
fn a_new_shape_gets_clone_box() {
    #[derive(Clone)]
    struct Sq(f64);
    impl Shape for Sq {
        fn area(&self) -> f64 {
            self.0 * self.0
        }
        fn name(&self) -> String {
            format!("sq({})", self.0)
        }
        fn scaled(&self, k: f64) -> Self {
            Sq(self.0 * k)
        }
    }
    let scene: Vec<Box<dyn Shape>> = vec![Box::new(Sq(3.0))];
    check!("scale_all([Sq(3)], 0.5)[0].area()", scale_all(&scene, 0.5)[0].area(), 2.25);
    check!("snapshot([Sq(3)])[0].name()", snapshot(&scene)[0].name(), "sq(3)");
}

use solution::*;

/// No derives at all.
struct Opaque;

#[test]
fn pixel_reused() {
    let p = Pixel { at: Point { x: 1, y: 2 }, rgb: [9, 9, 9] };
    check!(r#"trail(p, 3) with p = (1, 2), then p again"#, (trail(p, 3), p), (vec![Pixel { at: Point { x: 1, y: 2 }, rgb: [9, 9, 9] }, Pixel { at: Point { x: 2, y: 2 }, rgb: [9, 9, 9] }, Pixel { at: Point { x: 3, y: 2 }, rgb: [9, 9, 9] }], Pixel { at: Point { x: 1, y: 2 }, rgb: [9, 9, 9] }));
}

#[test]
fn fork_is_deep() {
    let s = Sprite { name: "hero".to_string(), at: Point { x: 0, y: 0 } };
    let (a, b) = fork(&s, Point { x: 5, y: 5 });
    check!(r#"fork a sprite named "hero" to (5, 5)"#, (a.name == b.name, a.name.as_ptr() != b.name.as_ptr(), b.at), (true, true, Point { x: 5, y: 5 }));
}

#[test]
fn common_opaque_ids() {
    let a: Vec<Id<Opaque>> = vec![Id::new(1), Id::new(2), Id::new(3)];
    let b: Vec<Id<Opaque>> = vec![Id::new(3), Id::new(1)];
    check!(r#"a = [1, 2, 3], b = [3, 1] as Id<Opaque>"#, common(&a, &b), vec![Id::new(1), Id::new(3)]);
}

#[test]
fn id_debug() {
    check!(r#"format!("{:?}", Id::<Opaque>::new(7))"#, format!("{:?}", Id::<Opaque>::new(7)), "Id(7)");
}

#[test]
fn id_in_hash_set() {
    let set: std::collections::HashSet<Id<Opaque>> = [Id::new(1), Id::new(2), Id::new(1)].into_iter().collect();
    check!(r#"Id<Opaque> 1, 2, 1 into a HashSet"#, set.len(), 2);
}

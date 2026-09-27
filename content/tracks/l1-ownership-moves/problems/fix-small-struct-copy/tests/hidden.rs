use solution::*;

/// No derives at all.
struct Opaque;

fn is_copy<T: Copy>(_: &T) -> bool {
    true
}

#[test]
fn copy_types() {
    let id: Id<String> = Id::new(1);
    check!("Point, Pixel and Id<String> are Copy", (is_copy(&Point { x: 0, y: 0 }), is_copy(&Pixel { at: Point { x: 0, y: 0 }, rgb: [0; 3] }), is_copy(&id)), (true, true, true));
}

#[test]
fn id_used_after_move() {
    let id: Id<Opaque> = Id::new(4);
    let v = vec![id, id];
    check!("vec![id, id], then id", (v, id), (vec![Id::new(4), Id::new(4)], Id::new(4)));
}

#[test]
fn trail_empty() {
    check!(r#"trail(p, 0)"#, trail(Pixel { at: Point { x: 0, y: 0 }, rgb: [1, 2, 3] }, 0), Vec::<Pixel>::new());
}

#[test]
fn point_debug() {
    check!(r#"format!("{:?}", Point { x: -1, y: 2 })"#, format!("{:?}", Point { x: -1, y: 2 }), "Point { x: -1, y: 2 }");
}

#[test]
fn fork_keeps_original() {
    let s = Sprite { name: "npc".to_string(), at: Point { x: 3, y: 4 } };
    let (a, _) = fork(&s, Point { x: 0, y: 0 });
    check!(r#"fork: the first sprite is unchanged"#, a, Sprite { name: "npc".to_string(), at: Point { x: 3, y: 4 } });
}

#[test]
fn sprite_clone_independent() {
    let s = Sprite { name: "orc".to_string(), at: Point { x: 0, y: 0 } };
    let mut c = s.clone();
    c.name.push('!');
    check!(r#"clone, then push to the clone's name"#, (s.name, c.name), ("orc".to_string(), "orc!".to_string()));
}

#[test]
fn common_none() {
    check!(r#"a = [1], b = [2]"#, common(&[Id::<Opaque>::new(1)], &[Id::new(2)]), Vec::<Id<Opaque>>::new());
}

#[test]
fn common_keeps_duplicates() {
    check!(r#"a = [5, 5, 6], b = [5]"#, common(&[Id::<Opaque>::new(5), Id::new(5), Id::new(6)], &[Id::new(5)]), vec![Id::new(5), Id::new(5)]);
}

#[test]
fn id_eq_by_raw() {
    check!(r#"Id::<Opaque>::new(3) == Id::new(3), != Id::new(4)"#, (Id::<Opaque>::new(3) == Id::new(3), Id::<Opaque>::new(3) != Id::new(4)), (true, true));
}

#[test]
fn id_debug_in_vec() {
    check!(r#"format!("{:?}", vec![Id::<Sprite>::new(0), Id::new(42)])"#, format!("{:?}", vec![Id::<Sprite>::new(0), Id::new(42)]), "[Id(0), Id(42)]");
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6102);
    for _ in 0..300 {
        let (x, y, n) = (rng.int(-50, 50) as i32, rng.int(-50, 50) as i32, rng.below(5) as i32);
        let rgb: Vec<u8> = rng.vec(3, 0, 255);
        let p = Pixel { at: Point { x, y }, rgb: [rgb[0], rgb[1], rgb[2]] };
        let want: Vec<Pixel> = (0..n).map(|i| Pixel { at: Point { x: x + i, y }, rgb: p.rgb }).collect();
        check!(format!("trail({p:?}, {n})"), trail(p, n), want);
        let la = rng.below(6);
        let lb = rng.below(6);
        let a: Vec<Id<Opaque>> = rng.vec::<u32>(la, 0, 5).into_iter().map(Id::new).collect();
        let b: Vec<Id<Opaque>> = rng.vec::<u32>(lb, 0, 5).into_iter().map(Id::new).collect();
        let want: Vec<Id<Opaque>> = a.iter().filter(|x| b.iter().any(|y| y.raw == x.raw)).map(|x| Id::new(x.raw)).collect();
        let set: std::collections::HashSet<Id<Opaque>> = a.iter().copied().collect();
        let distinct = { let mut r: Vec<u32> = a.iter().map(|x| x.raw).collect(); r.sort(); r.dedup(); r.len() };
        check!(format!("common({a:?}, {b:?}), distinct in a"), (common(&a, &b), set.len()), (want, distinct));
    }
}

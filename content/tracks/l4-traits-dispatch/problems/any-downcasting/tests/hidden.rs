use solution::*;

#[derive(Debug, PartialEq)]
struct Pos(i32, i32);
impl Component for Pos {
    fn name(&self) -> String {
        "pos".into()
    }
}

#[derive(Debug, PartialEq)]
struct Health(u32);
impl Component for Health {
    fn name(&self) -> String {
        format!("health {}", self.0)
    }
}

#[derive(Debug, PartialEq)]
struct Tag<T>(T);
impl<T: std::fmt::Debug + 'static> Component for Tag<T> {
    fn name(&self) -> String {
        format!("tag {:?}", self.0)
    }
}

#[test]
fn replace_keeps_position() {
    let mut e = Entity::default();
    e.insert(Pos(0, 0));
    e.insert(Health(1));
    e.insert(Tag("a"));
    e.insert(Health(2));
    check!(r#"insert Pos, Health(1), Tag("a"); replace Health(2)"#, e.names(), vec!["pos", "health 2", "tag \"a\""]);
}

#[test]
fn remove_keeps_order() {
    let mut e = Entity::default();
    e.insert(Pos(0, 0));
    e.insert(Health(9));
    e.insert(Tag(1u8));
    e.remove::<Health>();
    check!(r#"insert Pos, Health, Tag(1u8); remove Health"#, (e.names(), e.get::<Tag<u8>>()), (vec!["pos".to_string(), "tag 1".to_string()], Some(&Tag(1u8))));
}

#[test]
fn remove_missing() {
    check!(r#"remove::<Pos>() on empty"#, Entity::default().remove::<Pos>(), None);
}

#[test]
fn empty_names() {
    check!(r#"Entity::default().names()"#, Entity::default().names(), Vec::<String>::new());
}

#[test]
fn generic_types_are_distinct() {
    let mut e = Entity::default();
    e.insert(Tag(1u8));
    e.insert(Tag(2u16));
    check!(r#"Tag(1u8) and Tag(1u16)"#, (e.get::<Tag<u8>>(), e.get::<Tag<u16>>(), e.names().len()), (Some(&Tag(1u8)), Some(&Tag(2u16)), 2));
}

#[test]
fn insert_new_returns_none() {
    check!(r#"insert Pos into empty"#, Entity::default().insert(Pos(5, 5)), None);
}

#[test]
fn get_mut_missing() {
    check!(r#"get_mut::<Pos>() on empty"#, Entity::default().get_mut::<Pos>().is_none(), true);
}

#[test]
fn remove_then_insert_appends() {
    let mut e = Entity::default();
    e.insert(Pos(0, 0));
    e.insert(Health(3));
    e.remove::<Pos>();
    e.insert(Pos(1, 1));
    check!(r#"insert Pos, Health; remove Pos; insert Pos"#, e.names(), vec!["health 3", "pos"]);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(4409);
    for _ in 0..200 {
        let mut e = Entity::default();
        let mut model: Vec<(usize, i32)> = Vec::new();
        let mut log = Vec::new();
        for _ in 0..10 {
            let kind = rng.below(3);
            let v = rng.int(0, 9) as i32;
            let pos = model.iter().position(|&(k, _)| k == kind);
            if rng.below(3) == 0 {
                log.push(format!("remove {kind}"));
                let got = match kind {
                    0 => e.remove::<Pos>().map(|p| p.0),
                    1 => e.remove::<Health>().map(|h| h.0 as i32),
                    _ => e.remove::<Tag<i32>>().map(|t| t.0),
                };
                let want = pos.map(|i| model.remove(i).1);
                check!(log.join(", "), got, want);
            } else {
                log.push(format!("insert {kind}={v}"));
                let got = match kind {
                    0 => e.insert(Pos(v, 0)).map(|p| p.0),
                    1 => e.insert(Health(v as u32)).map(|h| h.0 as i32),
                    _ => e.insert(Tag(v)).map(|t| t.0),
                };
                let want = match pos {
                    Some(i) => Some(std::mem::replace(&mut model[i].1, v)),
                    None => {
                        model.push((kind, v));
                        None
                    }
                };
                check!(log.join(", "), got, want);
            }
            let want_names: Vec<String> = model.iter().map(|&(k, v)| match k { 0 => "pos".to_string(), 1 => format!("health {v}"), _ => format!("tag {v}") }).collect();
            check!(log.join(", "), e.names(), want_names);
        }
    }
}

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
fn insert_then_get() {
    let mut e = Entity::default();
    e.insert(Pos(1, 2));
    check!(r#"insert Pos(1, 2); get::<Pos>()"#, e.get::<Pos>(), Some(&Pos(1, 2)));
}

#[test]
fn missing_type() {
    let mut e = Entity::default();
    e.insert(Pos(0, 0));
    check!(r#"insert Pos; get::<Health>()"#, e.get::<Health>(), None);
}

#[test]
fn replace_returns_old() {
    let mut e = Entity::default();
    e.insert(Pos(1, 2));
    let old = e.insert(Pos(3, 4));
    check!(r#"insert Pos(1, 2), insert Pos(3, 4)"#, (old, e.get::<Pos>(), e.names()), (Some(Pos(1, 2)), Some(&Pos(3, 4)), vec!["pos".to_string()]));
}

#[test]
fn get_mut_edits() {
    let mut e = Entity::default();
    e.insert(Health(10));
    e.get_mut::<Health>().unwrap().0 += 5;
    check!(r#"get_mut::<Health>() then += 5"#, e.get::<Health>(), Some(&Health(15)));
}

#[test]
fn remove_by_value() {
    let mut e = Entity::default();
    e.insert(Health(7));
    check!(r#"insert Health(7), remove::<Health>()"#, (e.remove::<Health>(), e.get::<Health>()), (Some(Health(7)), None));
}

use solution::*;

#[test]
fn winner_mixed() {
    let ps: Vec<Box<dyn Player>> = vec![Box::new(Human::new("ann", 5)), Box::new(Team::new("a+b", 7)), Box::new(Human::new("bo", 6))];
    check!(r#"Human ann 5, Team a+b 7, Human bo 6"#, winner(&ps).map(|p| p.name()), Some("a+b".to_string()));
}

#[test]
fn beats_across_types() {
    check!(r#"Human zed 3 beats Team x+y 2"#, Human::new("zed", 3).beats(&Team::new("x+y", 2)), true);
}

#[test]
fn tie_broken_by_name() {
    check!(r#"Team b+c 4 vs Human al 4"#, (Team::new("b+c", 4).beats(&Human::new("al", 4)), Human::new("al", 4).beats(&Team::new("b+c", 4))), (false, true));
}

#[test]
fn exact_tie_first_wins() {
    let ps: Vec<Box<dyn Player>> = vec![Box::new(Human::new("x", 1)), Box::new(Human::new("x", 1))];
    check!(r#"two Humans "x" 1"#, std::ptr::addr_eq(winner(&ps).unwrap(), ps[0].as_ref()), true);
}

#[test]
fn no_players() {
    check!(r#"winner(&[])"#, winner(&[]).is_none(), true);
}

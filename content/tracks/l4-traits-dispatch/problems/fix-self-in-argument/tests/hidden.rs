use solution::*;

#[test]
fn never_beats_itself() {
    let h = Human::new("a", 1);
    check!(r#"h.beats(&h)"#, h.beats(&h), false);
}

#[test]
fn team_new_splits() {
    check!(r#"Team::new("p+q+r", 0).members"#, Team::new("p+q+r", 0).members, vec!["p", "q", "r"]);
}

#[test]
fn single_player() {
    let ps: Vec<Box<dyn Player>> = vec![Box::new(Team::new("solo", 9))];
    check!(r#"one Team"#, winner(&ps).map(|p| p.score()), Some(9));
}

#[test]
fn winner_by_name() {
    let ps: Vec<Box<dyn Player>> = vec![Box::new(Human::new("dan", 2)), Box::new(Team::new("b+z", 2)), Box::new(Human::new("cat", 2))];
    check!(r#"scores all 2: dan, b+z, cat"#, winner(&ps).map(|p| p.name()), Some("b+z".to_string()));
}

#[test]
fn winner_last() {
    let ps: Vec<Box<dyn Player>> = vec![Box::new(Human::new("a", 1)), Box::new(Human::new("b", 2)), Box::new(Human::new("c", 3))];
    check!(r#"scores 1, 2, 3"#, winner(&ps).map(|p| p.name()), Some("c".to_string()));
}

#[test]
fn zero_scores() {
    let ps: Vec<Box<dyn Player>> = vec![Box::new(Human::new("m", 0)), Box::new(Human::new("n", 0))];
    check!(r#"scores 0, 0"#, winner(&ps).map(|p| p.name()), Some("m".to_string()));
}

#[test]
fn dyn_beats_dyn() {
    let ps: Vec<Box<dyn Player>> = vec![Box::new(Human::new("a", u32::MAX)), Box::new(Team::new("b", 0))];
    check!(r#"ps[0].beats(ps[1].as_ref())"#, ps[0].beats(ps[1].as_ref()), true);
}

#[test]
fn a_new_player_type() {
    // Constructors stay available on concrete types.
    struct Bot(u32);
    impl Player for Bot {
        fn new(_name: &str, score: u32) -> Self {
            Bot(score)
        }
        fn name(&self) -> String {
            format!("bot{}", self.0)
        }
        fn score(&self) -> u32 {
            self.0
        }
    }
    let ps: Vec<Box<dyn Player>> = vec![Box::new(Human::new("h", 4)), Box::new(Bot::new("", 4))];
    check!("Human h 4, Bot 4", winner(&ps).map(|p| p.name()), Some("bot4".to_string()));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4411);
    for _ in 0..300 {
        let n = rng.below(6);
        let specs: Vec<(String, u32, bool)> = (0..n).map(|_| (rng.string(1, "ab"), rng.below(3) as u32, rng.bool())).collect();
        let ps: Vec<Box<dyn Player>> = specs
            .iter()
            .map(|(name, score, team)| if *team { Box::new(Team::new(name, *score)) as Box<dyn Player> } else { Box::new(Human::new(name, *score)) })
            .collect();
        let mut best: Option<usize> = None;
        for (i, (name, score, _)) in specs.iter().enumerate() {
            if best.map_or(true, |b| *score > specs[b].1 || (*score == specs[b].1 && *name < specs[b].0)) {
                best = Some(i);
            }
        }
        let got = winner(&ps).map(|w| ps.iter().position(|p| std::ptr::addr_eq(p.as_ref(), w)).unwrap());
        check!(format!("players = {specs:?}"), got, best);
    }
}

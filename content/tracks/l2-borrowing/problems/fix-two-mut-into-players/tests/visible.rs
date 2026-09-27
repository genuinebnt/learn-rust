use solution::*;

#[test]
fn transfer_and_finish() {
    let mut players = vec![Player { name: "ann".into(), score: 10 }, Player { name: "bo".into(), score: 3 }];
    let mut log = String::new();
    let (ps, moved) = {
        let mut r = Round::new(&mut players, &mut log);
        let moved = r.transfer(0, 1, 4);
        (r.finish(), moved)
    };
    check!(r#"ann 10, bo 3; transfer 0 -> 1, 4; finish"#, (ps.iter().map(|p| p.score).collect::<Vec<_>>(), moved), (vec![6, 7], 4));
}

#[test]
fn log_lines() {
    let mut players = vec![Player { name: "ann".into(), score: 10 }, Player { name: "bo".into(), score: 3 }];
    let mut log = String::new();
    {
        let mut r = Round::new(&mut players, &mut log);
        r.transfer(1, 0, 3);
        r.rename(1, "cy");
        r.finish();
    }
    check!(r#"ann 10, bo 3; transfer 1 -> 0, 3; rename 1 to "cy"; finish"#, log, "bo -> ann: 3\nbo is now cy\nround over\n".to_string());
}

#[test]
fn transfer_is_capped() {
    let mut players = vec![Player { name: "ann".into(), score: 10 }, Player { name: "bo".into(), score: 3 }];
    let mut log = String::new();
    let moved = Round::new(&mut players, &mut log).transfer(1, 0, 50);
    check!(r#"ann 10, bo 3; transfer 1 -> 0, 50"#, (moved, players[0].score, players[1].score), (3, 13, 0));
}

#[test]
fn same_player() {
    let mut players = vec![Player { name: "ann".into(), score: 10 }, Player { name: "bo".into(), score: 3 }];
    let mut log = String::new();
    let moved = Round::new(&mut players, &mut log).transfer(0, 0, 5);
    check!(r#"ann 10; transfer 0 -> 0, 5"#, (moved, players[0].score, log), (5, 10, "ann -> ann: 5\n".to_string()));
}

#[test]
fn players_outlive_the_round() {
    let mut players = vec![Player { name: "ann".into(), score: 10 }, Player { name: "bo".into(), score: 3 }];
    let mut log = String::new();
    let ps = Round::new(&mut players, &mut log).finish();
    ps[0].name = "zed".to_string();
    ps[1].score = 99;
    check!(r#"finish, then edit the players through the returned slice"#, (players[0].name.clone(), players[1].score), ("zed".to_string(), 99));
}

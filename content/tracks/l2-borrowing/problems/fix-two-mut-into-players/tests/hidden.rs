use solution::*;

#[test]
fn zero_points() {
    let mut players = vec![Player { name: "ann".into(), score: 10 }, Player { name: "bo".into(), score: 3 }];
    let mut log = String::new();
    let moved = Round::new(&mut players, &mut log).transfer(0, 1, 0);
    check!(r#"transfer 0 -> 1, 0"#, (moved, players[0].score, log), (0, 10, "ann -> bo: 0\n".to_string()));
}

#[test]
fn from_empty_player() {
    let mut players = vec![Player { name: "ann".into(), score: 10 }, Player { name: "bo".into(), score: 3 }];
    let mut log = String::new();
    players[1].score = 0;
    let moved = Round::new(&mut players, &mut log).transfer(1, 0, 5);
    check!(r#"bo 0; transfer 1 -> 0, 5"#, (moved, players[0].score), (0, 10));
}

#[test]
fn exact_balance() {
    let mut players = vec![Player { name: "ann".into(), score: 10 }, Player { name: "bo".into(), score: 3 }];
    let mut log = String::new();
    let moved = Round::new(&mut players, &mut log).transfer(1, 0, 3);
    check!(r#"transfer 1 -> 0, 3"#, (moved, players[1].score), (3, 0));
}

#[test]
fn rename_twice() {
    let mut players = vec![Player { name: "ann".into(), score: 10 }, Player { name: "bo".into(), score: 3 }];
    let mut log = String::new();
    {
        let mut r = Round::new(&mut players, &mut log);
        r.rename(0, "x");
        r.rename(0, "y");
    }
    check!(r#"rename 0 to x, then y"#, (players[0].name.clone(), log), ("y".to_string(), "ann is now x\nx is now y\n".to_string()));
}

#[test]
fn rename_empty() {
    let mut players = vec![Player { name: "ann".into(), score: 10 }, Player { name: "bo".into(), score: 3 }];
    let mut log = String::new();
    Round::new(&mut players, &mut log).rename(1, "");
    check!(r#"rename 1 to """#, log, "bo is now \n".to_string());
}

#[test]
fn log_is_appended() {
    let mut players = vec![Player { name: "ann".into(), score: 10 }, Player { name: "bo".into(), score: 3 }];
    let mut log = String::new();
    log.push_str("start\n");
    Round::new(&mut players, &mut log).finish();
    check!(r#"log starts "start\n"; finish"#, log, "start\nround over\n".to_string());
}

#[test]
fn transfer_after_rename_uses_new_name() {
    let mut players = vec![Player { name: "ann".into(), score: 10 }, Player { name: "bo".into(), score: 3 }];
    let mut log = String::new();
    {
        let mut r = Round::new(&mut players, &mut log);
        r.rename(0, "al");
        r.transfer(0, 1, 1);
    }
    check!(r#"rename 0 to "al"; transfer 0 -> 1, 1"#, log, "ann is now al\nal -> bo: 1\n".to_string());
}

#[test]
fn no_log_without_calls() {
    let mut players = vec![Player { name: "ann".into(), score: 10 }, Player { name: "bo".into(), score: 3 }];
    let mut log = String::new();
    let _ = Round::new(&mut players, &mut log);
    check!(r#"new round, dropped"#, log.len(), 0);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6215);
    for _ in 0..300 {
        let n = 1 + rng.below(4);
        let start: Vec<u32> = rng.vec(n, 0, 9);
        let mut players: Vec<Player> = start.iter().enumerate().map(|(i, &s)| Player { name: format!("p{i}"), score: s }).collect();
        let mut model = start.clone();
        let mut want_log = String::new();
        let mut log = String::new();
        let mut ops = Vec::new();
        let mut moves = Vec::new();
        {
            let mut r = Round::new(&mut players, &mut log);
            for _ in 0..5 {
                let (f, t, pts) = (rng.below(n), rng.below(n), rng.below(8) as u32);
                let moved = pts.min(model[f]);
                model[f] -= moved;
                model[t] += moved;
                want_log.push_str(&format!("p{f} -> p{t}: {moved}\n"));
                ops.push(format!("transfer {f} -> {t}, {pts}"));
                moves.push((r.transfer(f, t, pts), moved));
            }
            let ps = r.finish();
            want_log.push_str("round over\n");
            let got: Vec<u32> = ps.iter().map(|p| p.score).collect();
            check!(format!("scores {start:?}; {}", ops.join(", ")), got, model.clone());
        }
        check!(format!("scores {start:?}; {}; moved and log", ops.join(", ")), (moves.iter().map(|m| m.0).collect::<Vec<_>>(), log), (moves.iter().map(|m| m.1).collect::<Vec<_>>(), want_log));
    }
}

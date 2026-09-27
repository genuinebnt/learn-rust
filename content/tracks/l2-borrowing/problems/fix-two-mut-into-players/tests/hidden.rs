use solution::*;

#[test]
fn three_players() {
    check!(r#"scores [5, 5, 5], move 3 from 2 to 0"#, { let mut p = [Player { score: 5 }, Player { score: 5 }, Player { score: 5 }]; transfer(&mut p, 2, 0, 3); (p[0].score, p[1].score, p[2].score) }, (8, 5, 2));
}

#[test]
fn all_points() {
    check!(r#"scores [7, 0], move 7 from 0 to 1"#, { let mut p = [Player { score: 7 }, Player { score: 0 }]; transfer(&mut p, 0, 1, 7); (p[0].score, p[1].score) }, (0, 7));
}

#[test]
fn u32_max() {
    check!(r#"scores [u32::MAX, 0], move all"#, { let mut p = [Player { score: u32::MAX }, Player { score: 0 }]; transfer(&mut p, 0, 1, u32::MAX); (p[0].score, p[1].score) }, (0, u32::MAX));
}

#[test]
fn repeated() {
    check!(r#"scores [0, 9], move 3 from 1 to 0, three times"#, { let mut p = [Player { score: 0 }, Player { score: 9 }]; for _ in 0..3 { transfer(&mut p, 1, 0, 3); } (p[0].score, p[1].score) }, (9, 0));
}

#[test]
fn same_player_full() {
    check!(r#"scores [u32::MAX], move 5 from 0 to 0"#, { let mut p = [Player { score: u32::MAX }]; transfer(&mut p, 0, 0, 5); p[0].score }, u32::MAX);
}

#[test]
fn same_player_all() {
    check!(r#"scores [4], move 4 from 0 to 0"#, { let mut p = [Player { score: 4 }]; transfer(&mut p, 0, 0, 4); p[0].score }, 4);
}

#[test]
fn in_a_vec() {
    check!(r#"1000 players with 1 point; move from 999 to 0"#, { let mut p: Vec<Player> = (0..1000).map(|_| Player { score: 1 }).collect(); transfer(&mut p, 999, 0, 1); (p[0].score, p[999].score) }, (2, 0));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2014);
    for _ in 0..300 {
        let n = 1 + rng.below(5);
        let scores: Vec<u32> = rng.vec(n, 0, 20);
        let from = rng.below(n);
        let to = rng.below(n);
        let points = rng.int(0, scores[from] as i64) as u32;
        let mut p: Vec<Player> = scores.iter().map(|&s| Player { score: s }).collect();
        transfer(&mut p, from, to, points);
        let mut want = scores.clone();
        want[from] -= points;
        want[to] += points;
        check!(format!("scores {scores:?}, move {points} from {from} to {to}"), p.iter().map(|x| x.score).collect::<Vec<_>>(), want);
    }
}

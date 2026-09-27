use solution::*;

#[test]
fn moves() {
    check!(r#"scores [10, 0], move 4 from 0 to 1"#, { let mut p = [Player { score: 10 }, Player { score: 0 }]; transfer(&mut p, 0, 1, 4); (p[0].score, p[1].score) }, (6, 4));
}

#[test]
fn backwards() {
    check!(r#"scores [0, 10], move 10 from 1 to 0"#, { let mut p = [Player { score: 0 }, Player { score: 10 }]; transfer(&mut p, 1, 0, 10); (p[0].score, p[1].score) }, (10, 0));
}

#[test]
fn zero_points() {
    check!(r#"scores [3, 4], move 0 from 0 to 1"#, { let mut p = [Player { score: 3 }, Player { score: 4 }]; transfer(&mut p, 0, 1, 0); (p[0].score, p[1].score) }, (3, 4));
}

#[test]
fn same_player() {
    check!(r#"scores [5], move 3 from 0 to 0"#, { let mut p = [Player { score: 5 }]; transfer(&mut p, 0, 0, 3); p[0].score }, 5);
}

#[test]
fn middle_untouched() {
    check!(r#"scores [1, 2, 3], move 1 from 0 to 2"#, { let mut p = [Player { score: 1 }, Player { score: 2 }, Player { score: 3 }]; transfer(&mut p, 0, 2, 1); (p[0].score, p[1].score, p[2].score) }, (0, 2, 4));
}

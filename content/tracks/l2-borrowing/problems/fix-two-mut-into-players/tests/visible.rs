use solution::*;

#[test]
fn moves() {
    check!(r#"scores [10, 0], move 4 from 0 to 1"#, { let mut p = [Player { score: 10 }, Player { score: 0 }]; transfer(&mut p, 0, 1, 4); (p[0].score, p[1].score) }, (6, 4));
}

#[test]
fn backwards() {
    check!(r#"scores [0, 10], move 10 from 1 to 0"#, { let mut p = [Player { score: 0 }, Player { score: 10 }]; transfer(&mut p, 1, 0, 10); (p[0].score, p[1].score) }, (10, 0));
}

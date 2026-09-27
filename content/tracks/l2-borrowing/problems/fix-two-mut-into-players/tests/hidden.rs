use solution::*;

#[test]
fn same_player() {
    check!(r#"scores [5], move 3 from 0 to 0"#, { let mut p = [Player { score: 5 }]; transfer(&mut p, 0, 0, 3); p[0].score }, 5);
}

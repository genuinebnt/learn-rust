use solution::*;

#[test]
fn one_disk() {
    check!(r#"n = 1"#, hanoi(1), vec![(0, 2)]);
}

#[test]
fn no_disks() {
    check!(r#"n = 0"#, hanoi(0), Vec::<(u8, u8)>::new());
}

#[test]
fn two_disks() {
    check!(r#"n = 2"#, hanoi(2), vec![(0, 1), (0, 2), (1, 2)]);
}

#[test]
fn three_disks() {
    check!(r#"n = 3"#, hanoi(3), vec![(0, 2), (0, 1), (2, 1), (0, 2), (1, 0), (1, 2), (0, 2)]);
}

#[test]
fn ten_disks_take_1023_moves() {
    check!(r#"n = 10"#, hanoi(10).len(), 1023);
}

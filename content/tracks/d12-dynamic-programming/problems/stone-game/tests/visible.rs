use solution::*;

#[test]
fn four_piles() {
    check!(r#"piles = [3, 7, 2, 3]"#, stone_game(&[3, 7, 2, 3]), (10, 5));
}

#[test]
fn leetcode_four() {
    check!(r#"piles = [5, 3, 4, 5]"#, stone_game(&[5, 3, 4, 5]), (9, 8));
}

#[test]
fn empty() {
    check!(r#"piles = []"#, stone_game(&[]), (0, 0));
}

#[test]
fn one_pile() {
    check!(r#"piles = [4]"#, stone_game(&[4]), (4, 0));
}

#[test]
fn two_piles() {
    check!(r#"piles = [1, 2]"#, stone_game(&[1, 2]), (2, 1));
}

#[test]
fn bob_can_win() {
    check!(r#"piles = [1, 100, 1]"#, stone_game(&[1, 100, 1]), (2, 100));
}

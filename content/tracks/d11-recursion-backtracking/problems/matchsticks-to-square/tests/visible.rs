use solution::*;

#[test]
fn leetcode_square() {
    check!(r#"matchsticks = [1, 1, 2, 2, 2]"#, makesquare(&[1, 1, 2, 2, 2]), true);
}

#[test]
fn leetcode_no_square() {
    check!(r#"matchsticks = [3, 3, 3, 3, 4]"#, makesquare(&[3, 3, 3, 3, 4]), false);
}

#[test]
fn four_equal() {
    check!(r#"matchsticks = [7, 7, 7, 7]"#, makesquare(&[7, 7, 7, 7]), true);
}

#[test]
fn too_few_sticks() {
    check!(r#"matchsticks = [4, 4, 4] (total 12, but only three sticks)"#, makesquare(&[4, 4, 4]), false);
}

#[test]
fn stick_longer_than_a_side() {
    check!(r#"matchsticks = [1, 1, 1, 9] (side would be 3)"#, makesquare(&[1, 1, 1, 9]), false);
}

#[test]
fn total_divides_but_no_split() {
    check!(r#"matchsticks = [3, 3, 3, 3, 2, 2] (side 4: each 3 needs a 1)"#, makesquare(&[3, 3, 3, 3, 2, 2]), false);
}

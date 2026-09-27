use solution::*;

#[test]
fn leetcode_three_by_three() {
    check!(r#"dungeon = [[-2, -3, 3], [-5, -10, 1], [10, 30, -5]]"#, calculate_minimum_hp(&[vec![-2, -3, 3], vec![-5, -10, 1], vec![10, 30, -5]]), 7);
}

#[test]
fn leetcode_one_room() {
    check!(r#"dungeon = [[0]]"#, calculate_minimum_hp(&[vec![0]]), 1);
}

#[test]
fn healing_room() {
    check!(r#"dungeon = [[100]] (health must start at least 1)"#, calculate_minimum_hp(&[vec![100]]), 1);
}

#[test]
fn hurting_room() {
    check!(r#"dungeon = [[-5]]"#, calculate_minimum_hp(&[vec![-5]]), 6);
}

#[test]
fn biggest_sum_is_not_safest() {
    check!(r#"dungeon = [[3, -20, 30], [-3, 4, 0]]"#, calculate_minimum_hp(&[vec![3, -20, 30], vec![-3, 4, 0]]), 1);
}

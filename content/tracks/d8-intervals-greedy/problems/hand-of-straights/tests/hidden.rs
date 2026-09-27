use solution::*;

#[test]
fn not_divisible() {
    check!(r#"hand = [1, 2, 3, 4], group_size = 3"#, is_n_straight_hand(&[1, 2, 3, 4], 3), false);
}

#[test]
fn top_of_i32() {
    check!(r#"hand = [2147483646, 2147483647], group_size = 2"#, is_n_straight_hand(&[i32::MAX - 1, i32::MAX], 2), true);
}

#[test]
fn run_past_i32_max() {
    check!(r#"hand = [2147483647, 2147483647], group_size = 2"#, is_n_straight_hand(&[i32::MAX, i32::MAX], 2), false);
}

#[test]
fn bottom_of_i32() {
    check!(r#"hand = [-2147483648, -2147483647], group_size = 2"#, is_n_straight_hand(&[i32::MIN, i32::MIN + 1], 2), true);
}

#[test]
fn negatives() {
    check!(r#"hand = [0, -1, -3, -2], group_size = 2"#, is_n_straight_hand(&[0, -1, -3, -2], 2), true);
}

#[test]
fn duplicate_start_short() {
    check!(r#"hand = [1, 1, 2, 2, 3, 4], group_size = 3"#, is_n_straight_hand(&[1, 1, 2, 2, 3, 4], 3), false);
}

#[test]
fn spaced_out() {
    check!(r#"hand = [8, 10, 12], group_size = 3"#, is_n_straight_hand(&[8, 10, 12], 3), false);
}

#[test]
fn group_bigger_than_hand() {
    check!(r#"hand = [1, 2], group_size = 3"#, is_n_straight_hand(&[1, 2], 3), false);
}

#[test]
fn one_group_of_all() {
    check!(r#"hand = [3, 1, 2], group_size = 3"#, is_n_straight_hand(&[3, 1, 2], 3), true);
}

#[test]
fn three_runs_of_four() {
    check!(r#"hand = [5, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12], group_size = 4"#, is_n_straight_hand(&[5, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12], 4), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(823);
    for _ in 0..400 {
        let size = 1 + rng.below(4);
        let groups = rng.below(4);
        let mut hand: Vec<i32> = Vec::new();
        for _ in 0..groups {
            let start = rng.int(-3, 5) as i32;
            hand.extend(start..start + size as i32);
        }
        if rng.bool() && !hand.is_empty() {
            let i = rng.below(hand.len());
            hand[i] = rng.int(-3, 8) as i32;
        }
        rng.shuffle(&mut hand);
        // Remove the smallest card's run one card at a time from a sorted Vec.
        let mut left = hand.clone();
        left.sort_unstable();
        let mut want = left.len() % size == 0;
        while want && !left.is_empty() {
            let first = left[0];
            for card in first..first + size as i32 {
                match left.iter().position(|&c| c == card) {
                    Some(i) => {
                        left.remove(i);
                    }
                    None => {
                        want = false;
                        break;
                    }
                }
            }
        }
        check!(format!("hand = {hand:?}, group_size = {size}"), is_n_straight_hand(&hand, size), want);
    }
}

#[test]
fn scale_200k() {
    let distinct: Vec<i32> = (0..200_000).rev().collect();
    let mut broken = distinct.clone();
    broken[0] = 0;
    let stacked: Vec<i32> = (0..200_000).map(|i| i % 1000).collect();
    check!(
        "199999 down to 0 in runs of 1000; the same with 199999 swapped for 0; 0..1000 two hundred times in runs of 1000",
        (is_n_straight_hand(&distinct, 1000), is_n_straight_hand(&broken, 1000), is_n_straight_hand(&stacked, 1000)),
        (true, false, true)
    );
}

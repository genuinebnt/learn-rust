use solution::*;

#[test]
fn one_room() {
    check!(r#"dungeon = [[0]]"#, calculate_minimum_hp(&[vec![0]]), 1);
}

#[test]
fn known_trap() {
    check!(r#"dungeon = [[1, -3, 3], [0, -2, 0], [-3, -3, -3]]"#, calculate_minimum_hp(&[vec![1, -3, 3], vec![0, -2, 0], vec![-3, -3, -3]]), 3);
}

#[test]
fn avoid_the_pit() {
    check!(r#"dungeon = [[0, 5], [-1000, 0]]"#, calculate_minimum_hp(&[vec![0, 5], vec![-1000, 0]]), 1);
}

#[test]
fn heal_comes_too_late() {
    check!(r#"dungeon = [[1, -2, 3], [2, -2, -2]]"#, calculate_minimum_hp(&[vec![1, -2, 3], vec![2, -2, -2]]), 2);
}

#[test]
fn one_row() {
    check!(r#"dungeon = [[-1000, -1000, -1000]]"#, calculate_minimum_hp(&[vec![-1000, -1000, -1000]]), 3001);
}

#[test]
fn one_column() {
    check!(r#"dungeon = [[2], [1]]"#, calculate_minimum_hp(&[vec![2], vec![1]]), 1);
}

#[test]
fn last_room_hurts() {
    check!(r#"dungeon = [[0, 0, 0], [1, 1, -1]]"#, calculate_minimum_hp(&[vec![0, 0, 0], vec![1, 1, -1]]), 1);
}

#[test]
fn worst_case() {
    check!(r#"dungeon = 500 × 500 of -1000"#, calculate_minimum_hp(&vec![vec![-1000; 500]; 500]), 999_001);
}

#[test]
fn random_vs_brute_force() {
    // Try every path; each needs 1 - (its lowest running total), at least 1.
    fn walk(d: &[Vec<i32>], i: usize, j: usize, sum: i64, low: i64, best: &mut i64) {
        let sum = sum + d[i][j] as i64;
        let low = low.min(sum);
        if i + 1 == d.len() && j + 1 == d[0].len() {
            *best = (*best).min((1 - low).max(1));
            return;
        }
        if i + 1 < d.len() {
            walk(d, i + 1, j, sum, low, best);
        }
        if j + 1 < d[0].len() {
            walk(d, i, j + 1, sum, low, best);
        }
    }
    let mut rng = anneal_prelude::Rng::new(1223);
    for _ in 0..300 {
        let m = rng.int(1, 5) as usize;
        let n = rng.int(1, 5) as usize;
        let d: Vec<Vec<i32>> = (0..m).map(|_| rng.vec(n, -10, 10)).collect();
        let mut want = i64::MAX;
        walk(&d, 0, 0, 0, i64::MAX, &mut want);
        check!(format!("dungeon = {d:?}"), calculate_minimum_hp(&d), want);
    }
}

#[test]
fn scale_500() {
    let d: Vec<Vec<i32>> = (0..500i32).map(|i| (0..500i32).map(|j| (i * 37 + j * 91) % 2001 - 1000).collect()).collect();
    check!("dungeon[i][j] = (37i + 91j) % 2001 - 1000, 500 × 500", calculate_minimum_hp(&d), 5996);
}

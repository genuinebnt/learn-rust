use solution::*;

#[test]
fn before_all() {
    check!(r#"[[5]], 1"#, search_matrix(&[vec![5]], 1), false);
}

#[test]
fn last_cell() {
    check!(r#"[[1,2],[3,4]], 4"#, search_matrix(&[vec![1, 2], vec![3, 4]], 4), true);
}

#[test]
fn empty() {
    check!(r#"[]"#, search_matrix(&[], 1), false);
}

#[test]
fn between_rows() {
    check!(r#"[[1,3],[7,9]], 5"#, search_matrix(&[vec![1, 3], vec![7, 9]], 5), false);
}

#[test]
fn single_column() {
    let m = [vec![1], vec![4], vec![9]];
    check!(r#"[[1],[4],[9]], 4 and 5"#, (search_matrix(&m, 4), search_matrix(&m, 5)), (true, false));
}

#[test]
fn extremes() {
    let m = [vec![i32::MIN, 0], vec![5, i32::MAX]];
    check!(r#"[[i32::MIN, 0],[5, i32::MAX]], i32::MIN and i32::MAX"#, (search_matrix(&m, i32::MIN), search_matrix(&m, i32::MAX)), (true, true));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(408);
    for _ in 0..400 {
        let (r, c) = (1 + rng.below(4), 1 + rng.below(4));
        let mut vals: Vec<i32> = rng.vec(r * c, -40, 40);
        vals.sort_unstable();
        let m: Vec<Vec<i32>> = vals.chunks(c).map(|ch| ch.to_vec()).collect();
        let target = rng.int(-42, 42) as i32;
        check!(format!("matrix = {m:?}, target = {target}"), search_matrix(&m, target), vals.contains(&target));
    }
}

#[test]
fn scale_tall_matrix() {
    // 100000 rows of two values each; 200000 lookups.
    let m: Vec<Vec<i32>> = (0..100_000).map(|i| vec![4 * i, 4 * i + 2]).collect();
    let found = (0..200_000).filter(|&t| search_matrix(&m, 2 * t)).count();
    check!("rows [4i, 4i + 2] for i < 100000; look up every even number below 400000", found, 200_000);
}

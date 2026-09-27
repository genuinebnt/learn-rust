use solution::*;

#[test]
fn no_stones() {
    check!(r#"stones = []"#, last_stone_weight_ii(&[]), 0);
}

#[test]
fn one_heavy() {
    check!(r#"stones = [100]"#, last_stone_weight_ii(&[100]), 100);
}

#[test]
fn pair() {
    check!(r#"stones = [1, 2]"#, last_stone_weight_ii(&[1, 2]), 1);
}

#[test]
fn three_equal() {
    check!(r#"stones = [3, 3, 3]"#, last_stone_weight_ii(&[3, 3, 3]), 3);
}

#[test]
fn splits_evenly() {
    check!(r#"stones = [1, 1, 4, 2, 2]"#, last_stone_weight_ii(&[1, 1, 4, 2, 2]), 0);
}

#[test]
fn hundred_max() {
    check!(r#"stones = [100; 100]"#, last_stone_weight_ii(&[100; 100]), 0);
}

#[test]
fn odd_count_max() {
    check!(r#"stones = [100; 99]"#, last_stone_weight_ii(&[100; 99]), 100);
}

#[test]
fn one_big_rest_small() {
    check!(r#"stones = [100, 1, 1, 1]"#, last_stone_weight_ii(&[100, 1, 1, 1]), 97);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1233);
    for _ in 0..300 {
        let n = rng.below(12);
        let stones: Vec<u32> = rng.vec(n, 1, 30);
        let total: i64 = stones.iter().map(|&x| x as i64).sum();
        let want = (0u32..(1 << n))
            .map(|mask| {
                let a: i64 = (0..n).filter(|&i| mask >> i & 1 == 1).map(|i| stones[i] as i64).sum();
                (total - 2 * a).unsigned_abs() as u32
            })
            .min()
            .unwrap();
        check!(format!("stones = {stones:?}"), last_stone_weight_ii(&stones), want);
    }
}

#[test]
fn scale_hundred() {
    let mut stones: Vec<u32> = (0..99u32).map(|i| i * 7919 % 50 * 2 + 2).collect();
    stones.push(1);
    check!("stones = 99 even weights ((7919·i) % 50 · 2 + 2) and a 1", last_stone_weight_ii(&stones), 1);
}

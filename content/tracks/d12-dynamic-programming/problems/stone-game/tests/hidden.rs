use solution::*;

#[test]
fn empty() {
    check!(r#"piles = []"#, stone_game(&[]), (0, 0));
}

#[test]
fn three() {
    check!(r#"piles = [2, 1, 1]"#, stone_game(&[2, 1, 1]), (3, 1));
}

#[test]
fn greedy_trap() {
    check!(r#"piles = [3, 9, 1, 2]"#, stone_game(&[3, 9, 1, 2]), (11, 4));
}

#[test]
fn ties() {
    check!(r#"piles = [5, 5, 5, 5]"#, stone_game(&[5, 5, 5, 5]), (10, 10));
}

#[test]
fn close() {
    check!(r#"piles = [7, 8, 8, 10]"#, stone_game(&[7, 8, 8, 10]), (18, 15));
}

#[test]
fn zeros() {
    check!(r#"piles = [0, 0, 0]"#, stone_game(&[0, 0, 0]), (0, 0));
}

#[test]
fn big() {
    check!(r#"piles = [10⁶; 1000]"#, stone_game(&[1_000_000; 1000]), (500_000_000, 500_000_000));
}

#[test]
fn random_vs_brute_force() {
    // Returns (mover's total, other's total).
    fn play(p: &[u32]) -> (u64, u64) {
        match p {
            [] => (0, 0),
            [first, .., last] => {
                let (other_l, me_l) = play(&p[1..]);
                let (other_r, me_r) = play(&p[..p.len() - 1]);
                let left = (*first as u64 + me_l, other_l);
                let right = (*last as u64 + me_r, other_r);
                if left.0 >= right.0 { left } else { right }
            }
            [x] => (*x as u64, 0),
        }
    }
    let mut rng = anneal_prelude::Rng::new(1242);
    for _ in 0..300 {
        let n = rng.below(12);
        let piles: Vec<u32> = rng.vec(n, 0, 20);
        check!(format!("piles = {piles:?}"), stone_game(&piles), play(&piles));
    }
}

#[test]
fn scale_1000() {
    let piles: Vec<u32> = (0..1000u32).map(|i| i * 7919 % 1000).collect();
    check!("piles[i] = (7919·i) % 1000, 1000 piles", stone_game(&piles), (250_000, 249_500));
}

use solution::*;

#[test]
fn two_different() {
    check!(r#"stones = [7, 3]"#, last_stone_weight(&[7, 3]), Some(4));
}

#[test]
fn three_equal() {
    check!(r#"stones = [1, 1, 1]"#, last_stone_weight(&[1, 1, 1]), Some(1));
}

#[test]
fn large_weights() {
    check!(r#"stones = [1000000000, 1]"#, last_stone_weight(&[1_000_000_000, 1]), Some(999_999_999));
}

#[test]
fn max_weights_cancel() {
    check!(r#"stones = [1000000000, 1000000000]"#, last_stone_weight(&[1_000_000_000, 1_000_000_000]), None);
}

#[test]
fn remainder_is_heaviest() {
    check!(r#"stones = [9, 1, 1] (8 goes back and beats 1)"#, last_stone_weight(&[9, 1, 1]), Some(7));
}

#[test]
fn ends_in_destruction() {
    check!(r#"stones = [2, 2, 1, 1]"#, last_stone_weight(&[2, 2, 1, 1]), None);
}

#[test]
fn sorted_input() {
    check!(r#"stones = [1, 2, 3, 4, 5]"#, last_stone_weight(&[1, 2, 3, 4, 5]), Some(1));
}

#[test]
fn many_ones() {
    check!(r#"stones = [1; 1001]"#, last_stone_weight(&vec![1; 1001]), Some(1));
}

#[test]
fn powers_of_two() {
    check!(r#"stones = [1, 2, 4, 8, 16]"#, last_stone_weight(&[1, 2, 4, 8, 16]), Some(1));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(703);
    for _ in 0..300 {
        let n = rng.below(10);
        let stones: Vec<u32> = rng.vec(n, 1, 12);
        let mut left = stones.clone();
        while left.len() > 1 {
            left.sort_unstable();
            let y = left.pop().unwrap();
            let x = left.pop().unwrap();
            if y > x {
                left.push(y - x);
            }
        }
        check!(format!("stones = {stones:?}"), last_stone_weight(&stones), left.first().copied());
    }
}

#[test]
fn scale_200k() {
    let mut rng = anneal_prelude::Rng::new(704);
    let stones: Vec<u32> = rng.vec(200_000, 1, 1_000_000_000);
    // Reference: the same game on a BTreeMap multiset (weight → count).
    let mut bag = std::collections::BTreeMap::new();
    for &s in &stones {
        *bag.entry(s).or_insert(0u32) += 1;
    }
    let take = |bag: &mut std::collections::BTreeMap<u32, u32>| {
        let mut e = bag.last_entry()?;
        let w = *e.key();
        *e.get_mut() -= 1;
        if *e.get() == 0 {
            e.remove();
        }
        Some(w)
    };
    let want = loop {
        let Some(y) = take(&mut bag) else { break None };
        let Some(x) = take(&mut bag) else { break Some(y) };
        if y > x {
            *bag.entry(y - x).or_insert(0) += 1;
        }
    };
    check!("stones = 200000 random weights in 1..=10⁹", last_stone_weight(&stones), want);
}

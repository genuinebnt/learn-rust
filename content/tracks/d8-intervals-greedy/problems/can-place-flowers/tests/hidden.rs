use solution::*;

fn bed(s: &str) -> Vec<bool> {
    s.bytes().map(|b| b == b'1').collect()
}

#[test]
fn three_empty() {
    check!(r#"bed = [0, 0, 0], n = 2"#, can_place_flowers(&bed("000"), 2), true);
}

#[test]
fn two_empty() {
    check!(r#"bed = [0, 0], n = 2"#, can_place_flowers(&bed("00"), 2), false);
}

#[test]
fn left_edge() {
    check!(r#"bed = [0, 0, 1], n = 1"#, can_place_flowers(&bed("001"), 1), true);
}

#[test]
fn right_edge() {
    check!(r#"bed = [1, 0, 0], n = 1"#, can_place_flowers(&bed("100"), 1), true);
}

#[test]
fn gap_of_one() {
    check!(r#"bed = [1, 0, 1], n = 1"#, can_place_flowers(&bed("101"), 1), false);
}

#[test]
fn between_is_blocked() {
    check!(r#"bed = [0, 1, 0], n = 1"#, can_place_flowers(&bed("010"), 1), false);
}

#[test]
fn five_empty() {
    check!(r#"bed = [0, 0, 0, 0, 0], n = 3"#, can_place_flowers(&bed("00000"), 3), true);
}

#[test]
fn four_inside() {
    check!(r#"bed = [1, 0, 0, 0, 0, 1], n = 2"#, can_place_flowers(&bed("100001"), 2), false);
}

#[test]
fn exactly_enough() {
    check!(r#"bed = [0, 0, 0, 1, 0, 0, 0, 0], n = 3"#, can_place_flowers(&bed("00010000"), 3), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(803);
    for _ in 0..300 {
        let len = rng.below(13);
        let mut plots = vec![false; len];
        for i in 0..len {
            if rng.below(3) == 0 && (i == 0 || !plots[i - 1]) {
                plots[i] = true;
            }
        }
        // The most flowers any set of empty plots can take.
        let mut most = 0;
        for mask in 0u32..1 << len {
            let ok = (0..len).all(|i| mask >> i & 1 == 0 || !plots[i])
                && (0..len).all(|i| {
                    let full = |j: usize| plots[j] || mask >> j & 1 == 1;
                    !(i + 1 < len && full(i) && full(i + 1))
                });
            if ok {
                most = most.max(mask.count_ones() as usize);
            }
        }
        let n = rng.below(len + 2);
        let shown: String = plots.iter().map(|&p| if p { '1' } else { '0' }).collect();
        check!(format!("bed = {shown}, n = {n}"), can_place_flowers(&plots, n), n <= most);
    }
}

#[test]
fn scale_200k() {
    let plots = vec![false; 200_000];
    check!("bed = 200000 empty plots, n = 100000 and 100001", (can_place_flowers(&plots, 100_000), can_place_flowers(&plots, 100_001)), (true, false));
}

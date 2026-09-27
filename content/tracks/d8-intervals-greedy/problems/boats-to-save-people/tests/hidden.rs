use solution::*;

#[test]
fn exact_pairs() {
    check!(r#"people = [2, 2, 2, 2], limit = 4"#, num_rescue_boats(&[2, 2, 2, 2], 4), 2);
}

#[test]
fn heaviest_alone() {
    check!(r#"people = [5, 1, 4, 2], limit = 5"#, num_rescue_boats(&[5, 1, 4, 2], 5), 3);
}

#[test]
fn lightest_pair_trap() {
    check!(r#"people = [1, 1, 2, 2], limit = 3"#, num_rescue_boats(&[1, 1, 2, 2], 3), 2);
}

#[test]
fn sum_past_u32() {
    check!(r#"people = [4294967295, 4294967295], limit = 4294967295"#, num_rescue_boats(&[u32::MAX, u32::MAX], u32::MAX), 2);
}

#[test]
fn max_limit_pair() {
    check!(r#"people = [4294967294, 1], limit = 4294967295"#, num_rescue_boats(&[u32::MAX - 1, 1], u32::MAX), 1);
}

#[test]
fn many_light() {
    check!(r#"people = [1; 1000], limit = 2"#, num_rescue_boats(&vec![1; 1000], 2), 500);
}

#[test]
fn all_heavy() {
    check!(r#"people = [3, 3, 3], limit = 5"#, num_rescue_boats(&[3, 3, 3], 5), 3);
}

#[test]
fn mixed() {
    check!(r#"people = [2, 49, 50, 51, 98], limit = 100"#, num_rescue_boats(&[2, 49, 50, 51, 98], 100), 3);
}

#[test]
fn odd_one_out() {
    check!(r#"people = [1, 2, 3, 4, 5], limit = 6"#, num_rescue_boats(&[1, 2, 3, 4, 5], 6), 3);
}

#[test]
fn random_vs_brute_force() {
    // The last person rides alone or with any partner that fits.
    fn fewest(left: &mut Vec<u32>, limit: u32) -> usize {
        let Some(first) = left.pop() else { return 0 };
        let mut out = 1 + fewest(left, limit);
        for j in 0..left.len() {
            if first + left[j] <= limit {
                let other = left.remove(j);
                out = out.min(1 + fewest(left, limit));
                left.insert(j, other);
            }
        }
        left.push(first);
        out
    }
    let mut rng = anneal_prelude::Rng::new(818);
    for _ in 0..300 {
        let n = rng.below(8);
        let limit = rng.int(1, 8) as u32;
        let people: Vec<u32> = rng.vec(n, 1, limit as i64);
        let want = fewest(&mut people.clone(), limit);
        check!(format!("people = {people:?}, limit = {limit}"), num_rescue_boats(&people, limit), want);
    }
}

#[test]
fn scale_200k() {
    let people: Vec<u32> = (1..=200_000).rev().collect();
    check!("people = 200000 down to 1, limit = 200001", num_rescue_boats(&people, 200_001), 100_000);
}

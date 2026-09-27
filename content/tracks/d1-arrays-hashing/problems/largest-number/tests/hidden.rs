use solution::*;

#[test]
fn zeros() {
    check!(r#"nums = [0, 0]"#, largest_number(&[0, 0]), "0");
}

#[test]
fn shared_prefix() {
    check!(r#"nums = [121, 12]"#, largest_number(&[121, 12]), "12121");
}

#[test]
fn single_zero() {
    check!(r#"nums = [0]"#, largest_number(&[0]), "0");
}

#[test]
fn single() {
    check!(r#"nums = [42]"#, largest_number(&[42]), "42");
}

#[test]
fn zeros_and_one() {
    check!(r#"nums = [0, 0, 1]"#, largest_number(&[0, 0, 1]), "100");
}

#[test]
fn three_thirty() {
    check!(r#"nums = [3, 30]"#, largest_number(&[3, 30]), "330");
}

#[test]
fn long_shared_prefix() {
    check!(r#"nums = [824, 8247]"#, largest_number(&[824, 8247]), "8248247");
}

#[test]
fn u32_max() {
    check!(r#"nums = [4294967295, 9]"#, largest_number(&[u32::MAX, 9]), "94294967295");
}

#[test]
fn random_vs_brute_force() {
    fn permutations(xs: &mut Vec<u32>, k: usize, best: &mut String) {
        if k == xs.len() {
            let s: String = xs.iter().map(|x| x.to_string()).collect();
            if s > *best {
                *best = s;
            }
            return;
        }
        for i in k..xs.len() {
            xs.swap(k, i);
            permutations(xs, k + 1, best);
            xs.swap(k, i);
        }
    }
    let mut rng = anneal_prelude::Rng::new(19);
    for _ in 0..200 {
        let n = 1 + rng.below(5);
        let nums: Vec<u32> = (0..n).map(|_| *rng.pick(&[0, 1, 3, 9, 10, 30, 34, 90, 99, 121, 12, 300])).collect();
        let mut best = String::new();
        permutations(&mut nums.clone(), 0, &mut best);
        if best.starts_with('0') {
            best = "0".into();
        }
        check!(format!("nums = {nums:?}"), largest_number(&nums), best);
    }
}

#[test]
fn scale_100k() {
    let nums: Vec<u32> = (0..100_000).collect();
    let out = largest_number(&nums);
    check!("nums = 0..100000", (out.len(), out.starts_with("99999999999999999998999979"), out.ends_with("1000100000")), (488_890, true, true));
}

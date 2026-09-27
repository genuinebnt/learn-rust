use solution::*;

#[test]
fn no_digits_big_n() {
    check!(r#"digits = [], n = 10^18"#, at_most_n_given_digit_set(&[], 1_000_000_000_000_000_000), 0);
}

#[test]
fn n_equals_the_digit() {
    check!(r#"digits = [5], n = 5"#, at_most_n_given_digit_set(&[5], 5), 1);
}

#[test]
fn n_below_every_digit() {
    check!(r#"digits = [5], n = 4"#, at_most_n_given_digit_set(&[5], 4), 0);
}

#[test]
fn one_digit_n() {
    check!(r#"digits = [3, 4, 8], n = 4"#, at_most_n_given_digit_set(&[3, 4, 8], 4), 2);
}

#[test]
fn ones_up_to_10_18() {
    check!(r#"digits = [1], n = 10^18"#, at_most_n_given_digit_set(&[1], 1_000_000_000_000_000_000), 18);
}

#[test]
fn prefix_matches_then_misses() {
    check!(r#"digits = [1, 7, 9], n = 555555555555555555"#, at_most_n_given_digit_set(&[1, 7, 9], 555_555_555_555_555_555), 322_850_406);
}

#[test]
fn all_nines() {
    check!(r#"digits = [2, 9], n = 999999999999999999"#, at_most_n_given_digit_set(&[2, 9], 999_999_999_999_999_999), 524_286);
}

#[test]
fn n_made_of_digits() {
    check!(r#"digits = [6], n = 6666666666"#, at_most_n_given_digit_set(&[6], 6_666_666_666), 10);
}

#[test]
fn alternating() {
    check!(r#"digits = [1, 2], n = 12121212121212121"#, at_most_n_given_digit_set(&[1, 2], 12_121_212_121_212_121), 174_761);
}

#[test]
fn every_digit_10_18() {
    check!(r#"digits = [1..=9], n = 10^18"#, at_most_n_given_digit_set(&[1, 2, 3, 4, 5, 6, 7, 8, 9], 1_000_000_000_000_000_000), 168_856_464_709_124_010);
}

#[test]
fn every_digit_u64_max() {
    check!(r#"digits = [1..=9], n = u64::MAX"#, at_most_n_given_digit_set(&[1, 2, 3, 4, 5, 6, 7, 8, 9], u64::MAX), 2_627_136_424_427_962_617);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1247);
    for _ in 0..300 {
        let digits: Vec<u8> = (1..=9u8).filter(|_| rng.below(3) == 0).collect();
        let n = rng.int(1, 3000) as u64;
        let want = (1..=n).filter(|&x| x.to_string().bytes().all(|b| digits.contains(&(b - b'0')))).count() as u64;
        check!(format!("digits = {digits:?}, n = {n}"), at_most_n_given_digit_set(&digits, n), want);
    }
}

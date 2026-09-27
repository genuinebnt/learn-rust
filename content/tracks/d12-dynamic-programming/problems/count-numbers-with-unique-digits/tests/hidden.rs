use solution::*;

#[test]
fn zero() {
    check!(r#"n = 0"#, count_numbers_with_unique_digits(0), 1);
}

#[test]
fn four() {
    check!(r#"n = 4"#, count_numbers_with_unique_digits(4), 5275);
}

#[test]
fn eight() {
    check!(r#"n = 8"#, count_numbers_with_unique_digits(8), 2_345_851);
}

#[test]
fn nine() {
    check!(r#"n = 9"#, count_numbers_with_unique_digits(9), 5_611_771);
}

#[test]
fn ten() {
    check!(r#"n = 10"#, count_numbers_with_unique_digits(10), 8_877_691);
}

#[test]
fn twelve() {
    check!(r#"n = 12"#, count_numbers_with_unique_digits(12), 8_877_691);
}

#[test]
fn largest() {
    check!(r#"n = 20"#, count_numbers_with_unique_digits(20), 8_877_691);
}

#[test]
fn every_n_up_to_6_vs_brute_force() {
    let unique = |mut x: u32| {
        let mut seen = [false; 10];
        loop {
            let d = (x % 10) as usize;
            if seen[d] {
                return false;
            }
            seen[d] = true;
            x /= 10;
            if x == 0 {
                return true;
            }
        }
    };
    // want[k] = how many x < 10^k have unique digits, counted one number at a time.
    let mut want: Vec<u64> = Vec::new();
    let mut count = 0u64;
    let mut next_power = 1u32;
    for x in 0..=1_000_000u32 {
        if x == next_power {
            want.push(count);
            next_power *= 10;
        }
        count += unique(x) as u64;
    }
    for (n, &w) in want.iter().enumerate() {
        check!(format!("n = {n}"), count_numbers_with_unique_digits(n as u32), w);
    }
}

#[test]
fn every_n_up_to_20() {
    let mut want = 1u64;
    let mut of_length = 9u64;
    for n in 0..=20u32 {
        if n >= 1 {
            want += of_length;
            of_length *= 10u64.saturating_sub(n as u64);
        }
        check!(format!("n = {n}"), count_numbers_with_unique_digits(n), want);
    }
}

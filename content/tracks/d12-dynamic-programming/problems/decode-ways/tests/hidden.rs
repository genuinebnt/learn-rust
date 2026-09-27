use solution::*;

#[test]
fn single_zero() {
    check!(r#"s = "0""#, num_decodings("0"), 0);
}

#[test]
fn double_zero() {
    check!(r#"s = "100""#, num_decodings("100"), 0);
}

#[test]
fn zero_in_the_middle() {
    check!(r#"s = "101""#, num_decodings("101"), 1);
}

#[test]
fn thirty() {
    check!(r#"s = "230""#, num_decodings("230"), 0);
}

#[test]
fn thirty_first() {
    check!(r#"s = "301""#, num_decodings("301"), 0);
}

#[test]
fn leetcode_11106() {
    check!(r#"s = "11106""#, num_decodings("11106"), 2);
}

#[test]
fn ten_ones() {
    check!(r#"s = "1111111111""#, num_decodings("1111111111"), 89);
}

#[test]
fn mixed() {
    check!(r#"s = "2611055971756562""#, num_decodings("2611055971756562"), 4);
}

#[test]
fn tens_only() {
    check!(r#"s = "1010…10" (100 digits)"#, num_decodings(&"10".repeat(50)), 1);
}

#[test]
fn twenty_sevens() {
    check!(r#"s = "2727…27" (100 digits)"#, num_decodings(&"27".repeat(50)), 1);
}

#[test]
fn random_vs_brute_force() {
    fn count(d: &[u8]) -> u64 {
        if d.is_empty() {
            return 1;
        }
        let mut n = 0;
        if d[0] != b'0' {
            n += count(&d[1..]);
            if d.len() >= 2 && (d[0] - b'0') * 10 + (d[1] - b'0') <= 26 {
                n += count(&d[2..]);
            }
        }
        n
    }
    let mut rng = anneal_prelude::Rng::new(1208);
    for _ in 0..400 {
        let len = rng.int(1, 14) as usize;
        let s = rng.string(len, "0011122223456789");
        check!(format!("s = {s:?}"), num_decodings(&s), count(s.as_bytes()));
    }
}

#[test]
fn scale_ninety_ones() {
    // Plain recursion branches twice per digit here: about 10¹⁹ calls.
    let s = "1".repeat(90);
    check!("s = \"111…1\" (90 ones)", num_decodings(&s), 4_660_046_610_375_530_309);
}

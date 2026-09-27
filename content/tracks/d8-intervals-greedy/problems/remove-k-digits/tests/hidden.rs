use solution::*;

#[test]
fn repeat_then_rise() {
    check!(r#"num = "112", k = 1"#, remove_kdigits("112", 1), "11");
}

#[test]
fn falling() {
    check!(r#"num = "54321", k = 2"#, remove_kdigits("54321", 2), "321");
}

#[test]
fn only_zeros_left() {
    check!(r#"num = "100", k = 1"#, remove_kdigits("100", 1), "0");
}

#[test]
fn all_but_one() {
    check!(r#"num = "1234567890", k = 9"#, remove_kdigits("1234567890", 9), "0");
}

#[test]
fn all_same() {
    check!(r#"num = "1111", k = 2"#, remove_kdigits("1111", 2), "11");
}

#[test]
fn zeros_inside() {
    check!(r#"num = "10001", k = 1"#, remove_kdigits("10001", 1), "1");
}

#[test]
fn two_peaks() {
    check!(r#"num = "43214321", k = 4"#, remove_kdigits("43214321", 4), "1321");
}

#[test]
fn zero_alone() {
    check!(r#"num = "0", k = 0"#, remove_kdigits("0", 0), "0");
}

#[test]
fn equal_digits_stay() {
    check!(r#"num = "5337", k = 2"#, remove_kdigits("5337", 2), "33");
}

#[test]
fn peak_later() {
    check!(r#"num = "1173", k = 2"#, remove_kdigits("1173", 2), "11");
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(824);
    for _ in 0..400 {
        let len = 1 + rng.below(9);
        let mut num = rng.string(len, "0012349");
        if len > 1 && num.starts_with('0') {
            num.replace_range(0..1, "1");
        }
        let k = rng.below(len + 1);
        // Try every set of kept positions and keep the smallest value.
        let b = num.as_bytes();
        let mut want: Option<String> = None;
        for mask in 0u32..1 << len {
            if mask.count_ones() as usize != len - k {
                continue;
            }
            let kept: String = (0..len).filter(|&i| mask >> i & 1 == 1).map(|i| b[i] as char).collect();
            let trimmed = kept.trim_start_matches('0');
            let value = if trimmed.is_empty() { "0".to_string() } else { trimmed.to_string() };
            if want.as_ref().map_or(true, |w| (value.len(), &value) < (w.len(), w)) {
                want = Some(value);
            }
        }
        check!(format!("num = {num:?}, k = {k}"), remove_kdigits(&num, k), want.unwrap());
    }
}

#[test]
fn scale_200k() {
    let rising = format!("{}{}", "1".repeat(100_000), "9".repeat(100_000));
    let zeros = format!("1{}", "0".repeat(199_999));
    check!(
        "'1' × 100000 then '9' × 100000, k = 100000; '1' then '0' × 199999, k = 1",
        (remove_kdigits(&rising, 100_000) == "1".repeat(100_000), remove_kdigits(&zeros, 1)),
        (true, "0".to_string())
    );
}

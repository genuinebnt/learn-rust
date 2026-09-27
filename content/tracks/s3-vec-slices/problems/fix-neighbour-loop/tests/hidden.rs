use solution::*;

#[test]
fn deltas_single() {
    check!(r#"v = [5]"#, deltas(&[5]), Vec::<i64>::new());
}

#[test]
fn deltas_negative() {
    check!(r#"v = [3, -2, -2]"#, deltas(&[3, -2, -2]), vec![-5, 0]);
}

#[test]
fn peaks_short() {
    check!(r#"v = [], [1], [1, 2]"#, (peaks(&[]), peaks(&[1]), peaks(&[1, 2])), (vec![], vec![], vec![]));
}

#[test]
fn peaks_ends_never_count() {
    check!(r#"v = [9, 1, 9]"#, peaks(&[9, 1, 9]), Vec::<usize>::new());
}

#[test]
fn peaks_plateau_is_not_strict() {
    check!(r#"v = [1, 3, 3, 1]"#, peaks(&[1, 3, 3, 1]), Vec::<usize>::new());
}

#[test]
fn peaks_last_interior() {
    check!(r#"v = [0, 1, 0]"#, peaks(&[0, 1, 0]), vec![1]);
}

#[test]
fn sum16_empty() {
    check!(r#"bytes = []"#, sum16(&[]), 0x0000);
}

#[test]
fn sum16_one_byte() {
    check!(r#"bytes = [0xAB]"#, sum16(&[0xAB]), 0xAB00);
}

#[test]
fn sum16_even() {
    check!(r#"bytes = [0x12, 0x34, 0x56, 0x78]"#, sum16(&[0x12, 0x34, 0x56, 0x78]), 0x68AC);
}

#[test]
fn sum16_wraps() {
    check!(r#"bytes = [0xFF, 0xFF, 0x00, 0x02]"#, sum16(&[0xFF, 0xFF, 0x00, 0x02]), 0x0001);
}

#[test]
fn commas_short() {
    check!(r#""12""#, with_commas("12"), "12".to_string());
}

#[test]
fn commas_exact_three() {
    check!(r#""123""#, with_commas("123"), "123".to_string());
}

#[test]
fn commas_four() {
    check!(r#""1000""#, with_commas("1000"), "1,000".to_string());
}

#[test]
fn commas_six() {
    check!(r#""123456""#, with_commas("123456"), "123,456".to_string());
}

#[test]
fn commas_empty() {
    check!(r#""""#, with_commas(""), String::new());
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7305);
    for _ in 0..400 {
        let n = rng.below(9);
        let v: Vec<i64> = rng.vec(n, -5, 5);
        let w: Vec<i32> = v.iter().map(|&x| x as i32).collect();
        let want_d: Vec<i64> = (1..n).map(|i| v[i] - v[i - 1]).collect();
        let want_p: Vec<usize> = (1..n.saturating_sub(1)).filter(|&i| w[i - 1] < w[i] && w[i] > w[i + 1]).collect();
        let bytes: Vec<u8> = rng.vec(n, 0, 255);
        let mut want_s = 0u16;
        let mut i = 0;
        while i < n {
            let lo = if i + 1 < n { bytes[i + 1] } else { 0 };
            want_s = want_s.wrapping_add((bytes[i] as u16) << 8 | lo as u16);
            i += 2;
        }
        let digits: String = (0..n).map(|k| char::from(b'0' + (k % 10) as u8)).collect();
        let mut want_c = String::new();
        for (k, c) in digits.chars().enumerate() {
            if k > 0 && (n - k) % 3 == 0 {
                want_c.push(',');
            }
            want_c.push(c);
        }
        check!(format!("v = {v:?}, bytes = {bytes:?}, digits = {digits:?}"),
               (deltas(&v), peaks(&w), sum16(&bytes), with_commas(&digits)), (want_d, want_p, want_s, want_c));
    }
}

#[test]
fn scale_200k() {
    let v: Vec<i64> = (0..200_000).map(|i| i * i % 1000).collect();
    let w: Vec<i32> = (0..200_001).map(|i| if i % 2 == 1 { 1 } else { 0 }).collect();
    let bytes = vec![0xFFu8; 200_001];
    check!("200000 values", (deltas(&v).len(), peaks(&w).len(), sum16(&bytes), with_commas(&"9".repeat(200_000)).len()), (199_999, 100_000, 0x7860, 266_666));
}

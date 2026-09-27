use solution::*;

use std::time::Duration;

#[test]
fn find_empty() {
    check!(r#"find([], 0)"#, find(&[], 0), None);
}

#[test]
fn searching_for_minus_one() {
    check!(r#"find([5, -1], -1), find([0, 1], -1)"#, (find(&[5, -1], -1), find(&[0, 1], -1)), (Some(1), None));
}

#[test]
fn find_duplicates_give_the_first() {
    check!(r#"find([2, 5, 5, 5], 5)"#, find(&[2, 5, 5, 5], 5), Some(1));
}

#[test]
fn find_extremes() {
    check!(r#"find([i32::MIN, i32::MAX], i32::MAX)"#, find(&[i32::MIN, i32::MAX], i32::MAX), Some(1));
}

#[test]
fn rfind_is_a_byte_offset() {
    check!(r#"rfind("héllo wörld", 'ö')"#, rfind("héllo wörld", 'ö'), Some(8));
}

#[test]
fn rfind_empty_string() {
    check!(r#"rfind("", 'a')"#, rfind("", 'a'), None);
}

#[test]
fn rfind_multibyte_char() {
    check!(r#"rfind("🦀x🦀", '🦀')"#, rfind("🦀x🦀", '🦀'), Some(5));
}

#[test]
fn one_nanosecond() {
    check!(r#"Some(1 ns)"#, timeout_ms(Some(Duration::from_nanos(1))), 1);
}

#[test]
fn rounds_up_not_to_nearest() {
    check!(r#"Some(1.000001 ms), Some(1.999 ms), Some(2 ms)"#, (timeout_ms(Some(Duration::from_nanos(1_000_001))), timeout_ms(Some(Duration::from_micros(1999))), timeout_ms(Some(Duration::from_millis(2)))), (2, 2, 2));
}

#[test]
fn long_timeouts_clamp() {
    check!(r#"Some(Duration::MAX), Some(u64::MAX seconds)"#, (timeout_ms(Some(Duration::MAX)), timeout_ms(Some(Duration::from_secs(u64::MAX)))), (i64::MAX, i64::MAX));
}

#[test]
fn largest_exact_timeout() {
    check!(r#"Some(i64::MAX ms)"#, timeout_ms(Some(Duration::from_millis(i64::MAX as u64))), i64::MAX);
}

#[test]
fn just_past_i64_max_ms() {
    check!(r#"Some(i64::MAX ms + 1 ns)"#, timeout_ms(Some(Duration::from_millis(i64::MAX as u64) + Duration::from_nanos(1))), i64::MAX);
}

#[test]
fn a_day() {
    check!(r#"Some(1 day)"#, timeout_ms(Some(Duration::from_secs(86_400))), 86_400_000);
}

#[test]
fn large_index() {
    let v: Vec<i32> = (0..1_000_000).collect();
    check!(r#"v = 0..10⁶, x = 999999"#, find(&v, 999_999), Some(999_999));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7103);
    for _ in 0..400 {
        let n = rng.below(8);
        let v: Vec<i32> = rng.vec(n, -3, 3);
        let x = rng.int(-4, 4) as i32;
        check!(format!("find(v = {v:?}, x = {x})"), find(&v, x), v.iter().position(|&y| y == x));
        let len = rng.below(8);
        let s = rng.string(len, "ab/é");
        let c = *rng.pick(&['/', 'é', 'z']);
        let want = s.char_indices().filter(|&(_, ch)| ch == c).map(|(i, _)| i).last();
        check!(format!("rfind(s = {s:?}, c = {c:?})"), rfind(&s, c), want);
        let t = match rng.below(4) {
            0 => None,
            1 => Some(Duration::from_nanos(rng.int(0, 3_000_000) as u64)),
            2 => Some(Duration::new(rng.int(0, i64::MAX) as u64, rng.int(0, 999_999_999) as u32)),
            _ => Some(Duration::new(u64::MAX - rng.below(3) as u64, rng.int(0, 999_999_999) as u32)),
        };
        let want = match t {
            None => -1,
            Some(d) => {
                let ms = (d.as_nanos() + 999_999) / 1_000_000;
                if ms > i64::MAX as u128 { i64::MAX } else { ms as i64 }
            }
        };
        check!(format!("timeout_ms({t:?})"), timeout_ms(t), want);
    }
}

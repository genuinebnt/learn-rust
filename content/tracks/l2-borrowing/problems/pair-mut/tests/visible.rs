use solution::*;

#[test]
fn pair_swap() {
    check!(r#"v = [1, 2, 3], pair (0, 2), swap"#, { let mut v = [1, 2, 3]; if let Some((a, b)) = pair_mut(&mut v, 0, 2) { std::mem::swap(a, b); } v }, [3, 2, 1]);
}

#[test]
fn pair_order_kept() {
    check!(r#"v = [10, 20, 30], pair (2, 0)"#, { let mut v = [10, 20, 30]; let (a, b) = pair_mut(&mut v, 2, 0).unwrap(); (*a, *b) }, (30, 10));
}

#[test]
fn pair_none() {
    check!(r#"pair (1, 1) and (0, 5) of a 2-element slice"#, (pair_mut(&mut [1, 2], 1, 1).is_none(), pair_mut(&mut [1, 2], 0, 5).is_none()), (true, true));
}

#[test]
fn carry_digits() {
    check!(r#"digits [15, 9, 3] (least significant first), carry"#, { let mut v = [15u32, 9, 3]; for_each_adjacent_mut(&mut v, |a: &mut u32, b: &mut u32| { *b += *a / 10; *a %= 10; }); v }, [5, 0, 4]);
}

#[test]
fn bubble_pass() {
    check!(r#"one bubble pass over [3, 1, 2, 0]"#, { let mut v = [3, 1, 2, 0]; for_each_adjacent_mut(&mut v, |a: &mut i32, b: &mut i32| if *a > *b { std::mem::swap(a, b) }); v }, [1, 2, 0, 3]);
}

#[test]
fn short_slices() {
    check!(r#"for_each_adjacent_mut on [] and [7]: calls"#, { let mut n = 0; for_each_adjacent_mut(&mut [0u8; 0], |_, _| n += 1); for_each_adjacent_mut(&mut [7], |_, _| n += 1); n }, 0);
}

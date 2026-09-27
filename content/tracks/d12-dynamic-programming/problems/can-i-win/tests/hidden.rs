use solution::*;

#[test]
fn zero() {
    check!(r#"max_choosable = 1, desired_total = 0"#, can_i_win(1, 0), true);
}

#[test]
fn one_number_enough() {
    check!(r#"max_choosable = 1, desired_total = 1"#, can_i_win(1, 1), true);
}

#[test]
fn one_number_short() {
    check!(r#"max_choosable = 1, desired_total = 2"#, can_i_win(1, 2), false);
}

#[test]
fn three_to_five() {
    check!(r#"max_choosable = 3, desired_total = 5"#, can_i_win(3, 5), true);
}

#[test]
fn exact_sum_even_count() {
    check!(r#"max_choosable = 20, desired_total = 210"#, can_i_win(20, 210), false);
}

#[test]
fn exact_sum_odd_count() {
    check!(r#"max_choosable = 19, desired_total = 190"#, can_i_win(19, 190), true);
}

#[test]
fn too_big() {
    check!(r#"max_choosable = 20, desired_total = 300"#, can_i_win(20, 300), false);
}

#[test]
fn ten_forty() {
    check!(r#"max_choosable = 10, desired_total = 40"#, can_i_win(10, 40), false);
}

#[test]
fn twelve_forty_nine() {
    check!(r#"max_choosable = 12, desired_total = 49"#, can_i_win(12, 49), true);
}

#[test]
fn random_vs_brute_force() {
    fn wins(used: &mut Vec<bool>, left: i32) -> bool {
        for i in 0..used.len() {
            if !used[i] {
                if i as i32 + 1 >= left {
                    return true;
                }
                used[i] = true;
                let other = wins(used, left - i as i32 - 1);
                used[i] = false;
                if !other {
                    return true;
                }
            }
        }
        false
    }
    let mut rng = anneal_prelude::Rng::new(1248);
    for _ in 0..300 {
        let m = rng.int(1, 8) as u32;
        let d = rng.int(0, 40) as u32;
        let want = d == 0 || (m * (m + 1) / 2 >= d && wins(&mut vec![false; m as usize], d as i32));
        check!(format!("max_choosable = {m}, desired_total = {d}"), can_i_win(m, d), want);
    }
}

#[test]
fn scale_twenty() {
    check!("max_choosable = 20, desired_total = 152", can_i_win(20, 152), false);
    check!("max_choosable = 20, desired_total = 200", can_i_win(20, 200), false);
    check!("max_choosable = 20, desired_total = 160", can_i_win(20, 160), true);
    check!("max_choosable = 18, desired_total = 79", can_i_win(18, 79), true);
}

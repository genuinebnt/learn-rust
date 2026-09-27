use solution::*;

#[test]
fn single() {
    check!(r#"matchsticks = [1]"#, makesquare(&[1]), false);
}

#[test]
fn four_ones() {
    check!(r#"matchsticks = [1, 1, 1, 1]"#, makesquare(&[1, 1, 1, 1]), true);
}

#[test]
fn total_not_divisible() {
    check!(r#"matchsticks = [1, 1, 1, 1, 1]"#, makesquare(&[1, 1, 1, 1, 1]), false);
}

#[test]
fn three_per_side() {
    check!(r#"matchsticks = [5, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3]"#, makesquare(&[5, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3]), true);
}

#[test]
fn leetcode_fifteen() {
    check!(r#"matchsticks = [5, 5, 5, 5, 16, 4, 4, 4, 4, 4, 3, 3, 3, 3, 4]"#, makesquare(&[5, 5, 5, 5, 16, 4, 4, 4, 4, 4, 3, 3, 3, 3, 4]), false);
}

#[test]
fn first_fit_fails() {
    check!(r#"matchsticks = [13, 13, 6, 4, 6, 2, 5, 3] (side 13: 6+4+3 and 6+5+2)"#, makesquare(&[13, 13, 6, 4, 6, 2, 5, 3]), true);
}

#[test]
fn total_past_u32() {
    check!(r#"matchsticks = [10⁹; 16] (total 1.6·10¹⁰)"#, makesquare(&[1_000_000_000; 16]), true);
}

#[test]
fn total_past_u32_no_square() {
    check!(r#"matchsticks = [10⁹; 16] + [4]"#, makesquare(&[vec![1_000_000_000; 16], vec![4]].concat()), false);
}

#[test]
fn unsorted_input() {
    check!(r#"matchsticks = [2, 1, 2, 1, 2, 2, 1, 1]"#, makesquare(&[2, 1, 2, 1, 2, 2, 1, 1]), true);
}

/// Every way to give each stick one of the four sides.
fn brute(sticks: &[u32]) -> bool {
    (0..1usize << (2 * sticks.len())).any(|code| {
        let mut sides = [0u64; 4];
        for (i, &s) in sticks.iter().enumerate() {
            sides[code >> (2 * i) & 3] += u64::from(s);
        }
        sides[0] > 0 && sides.iter().all(|&x| x == sides[0])
    })
}

#[test]
fn random_vs_every_assignment() {
    let mut rng = anneal_prelude::Rng::new(1134);
    for _ in 0..300 {
        let mut sticks: Vec<u32> = Vec::new();
        if rng.bool() {
            let n = rng.int(1, 7) as usize;
            sticks = rng.vec(n, 1, 6);
        } else {
            // Four equal sides, some cut in two, sometimes with one stick made longer.
            let side = rng.int(2, 9) as u32;
            for _ in 0..4 {
                let cut = rng.int(0, side as i64 - 1) as u32;
                if cut > 0 && sticks.len() < 5 {
                    sticks.push(cut);
                    sticks.push(side - cut);
                } else {
                    sticks.push(side);
                }
            }
            if rng.bool() {
                let i = rng.below(sticks.len());
                sticks[i] += 1;
            }
            rng.shuffle(&mut sticks);
        }
        check!(format!("matchsticks = {sticks:?}"), makesquare(&sticks), brute(&sticks));
    }
}

#[test]
fn scale_twenty_sticks_no_square() {
    let sticks = [28, 318, 921, 8, 630, 3, 814, 403, 630, 379, 135, 834, 70, 36, 2, 47, 43, 918, 888, 913];
    check!(format!("matchsticks = {sticks:?}"), makesquare(&sticks), false);
}

#[test]
fn scale_twenty_sticks_square() {
    let sticks = [856, 133, 296, 248, 751, 605, 757, 480, 14, 204, 644, 412, 860, 37, 138, 82, 10, 332, 771, 106];
    check!(format!("matchsticks = {sticks:?}"), makesquare(&sticks), true);
}

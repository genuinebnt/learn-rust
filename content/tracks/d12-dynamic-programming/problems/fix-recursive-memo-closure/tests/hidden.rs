use solution::*;

#[test]
fn two_stairs() {
    check!(r#"n = 2"#, climb_ways(2), 2);
}

#[test]
fn five() {
    check!(r#"n = 5"#, climb_ways(5), 13);
}

#[test]
fn seven() {
    check!(r#"n = 7"#, climb_ways(7), 44);
}

#[test]
fn seventy() {
    check!(r#"n = 70"#, climb_ways(70), 2_073_693_258_389_777_176);
}

#[test]
fn largest() {
    check!(r#"n = 73"#, climb_ways(73), 12_903_063_846_126_135_669);
}

#[test]
fn zero() {
    check!(r#"n = 0"#, climb_ways(0), 1);
}

#[test]
fn twice() {
    check!(r#"n = 60, asked twice"#, (climb_ways(60), climb_ways(60)), (4_680_045_560_037_375, 4_680_045_560_037_375));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1255);
    for _ in 0..200 {
        let n = rng.int(0, 73) as u64;
        let mut w = [1u64, 1, 2];
        for _ in 2..n {
            w = [w[1], w[2], w[0] + w[1] + w[2]];
        }
        let want = if n < 3 { w[n as usize] } else { w[2] };
        check!(format!("n = {n}"), climb_ways(n), want);
    }
}

#[test]
fn every_n_up_to_73() {
    let mut w = vec![1u64, 1, 2];
    for k in 3..=73 {
        w.push(w[k - 1] + w[k - 2] + w[k - 3]);
    }
    for n in 0..=73 {
        check!(format!("n = {n}"), climb_ways(n as u64), w[n]);
    }
}

use solution::*;

#[test]
fn target_is_a_deadend() {
    check!(r#"deadends = ["0001"], target = "0001""#, open_lock(&["0001"], "0001"), None);
}

#[test]
fn farthest_combination() {
    check!(r#"deadends = [], target = "5555""#, open_lock(&[], "5555"), Some(20));
}

#[test]
fn wrap_on_every_wheel() {
    check!(r#"deadends = [], target = "9999""#, open_lock(&[], "9999"), Some(4));
}

#[test]
fn detour_around_one_wheel() {
    check!(r#"deadends = ["0001", "0009"], target = "0002""#, open_lock(&["0001", "0009"], "0002"), Some(4));
}

#[test]
fn duplicate_deadends() {
    check!(r#"deadends = ["1000", "1000"], target = "1000""#, open_lock(&["1000", "1000"], "1000"), None);
}

#[test]
fn deadend_on_the_direct_path() {
    check!(r#"deadends = ["0100"], target = "0200""#, open_lock(&["0100"], "0200"), Some(4));
}

#[test]
fn mixed_directions() {
    check!(r#"deadends = [], target = "1928""#, open_lock(&[], "1928"), Some(6));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(944);
    for _ in 0..40 {
        let k = rng.below(60);
        let dead: Vec<String> = (0..k).map(|_| rng.string(4, "0123")).collect();
        let target = rng.string(4, "01239");
        let refs: Vec<&str> = dead.iter().map(|s| s.as_str()).collect();
        // Brute force: relax distances over all 10000 combinations until they settle.
        let digits = |s: &str| -> [u8; 4] { let b = s.as_bytes(); [b[0] - b'0', b[1] - b'0', b[2] - b'0', b[3] - b'0'] };
        let blocked: Vec<[u8; 4]> = dead.iter().map(|s| digits(s)).collect();
        let mut dist = std::collections::HashMap::from([([0u8; 4], 0u32)]);
        if blocked.contains(&[0; 4]) {
            dist.clear();
        }
        let mut frontier: Vec<[u8; 4]> = dist.keys().copied().collect();
        while !frontier.is_empty() {
            let mut next = Vec::new();
            for s in frontier {
                for i in 0..4 {
                    for step in [1, 9] {
                        let mut t = s;
                        t[i] = (t[i] + step) % 10;
                        if !blocked.contains(&t) && !dist.contains_key(&t) {
                            dist.insert(t, dist[&s] + 1);
                            next.push(t);
                        }
                    }
                }
            }
            frontier = next;
        }
        let want = dist.get(&digits(&target)).copied();
        check!(format!("deadends = {dead:?}, target = {target:?}"), open_lock(&refs, &target), want);
    }
}

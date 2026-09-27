use solution::*;

#[test]
fn self_loop() {
    check!(r#"0→0"#, cycle_start(&[Some(0)], Some(0)), Some(0));
}

#[test]
fn empty() {
    check!(r#"no head"#, cycle_start(&[], None), None);
}

#[test]
fn head_not_zero() {
    check!(r#"3→1→2→1, node 0 unused"#, cycle_start(&[None, Some(2), Some(1), Some(1)], Some(3)), Some(1));
}

#[test]
fn tail_self_loop() {
    check!(r#"0→1→2→2"#, cycle_start(&[Some(1), Some(2), Some(2)], Some(0)), Some(2));
}

#[test]
fn cycle_elsewhere() {
    check!(r#"head 0→1→end; 2→3→2 is not reachable"#, cycle_start(&[Some(1), None, Some(3), Some(2)], Some(0)), None);
}

#[test]
fn whole_list_is_cycle() {
    check!(r#"0→1→2→3→4→0"#, cycle_start(&[Some(1), Some(2), Some(3), Some(4), Some(0)], Some(0)), Some(0));
}

#[test]
fn long_tail_short_cycle() {
    let mut next: Vec<Option<usize>> = (1..=1000).map(Some).collect();
    next[999] = Some(998);
    check!(r#"0→1→…→999→998"#, cycle_start(&next, Some(0)), Some(998));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(510);
    for _ in 0..300 {
        let n = 1 + rng.below(10);
        let next: Vec<Option<usize>> = (0..n).map(|_| if rng.below(4) == 0 { None } else { Some(rng.below(n)) }).collect();
        let head = if rng.below(10) == 0 { None } else { Some(rng.below(n)) };
        // Reference: walk and remember when each node was first seen.
        let mut seen = vec![false; n];
        let mut cur = head;
        let mut want = None;
        while let Some(i) = cur {
            if seen[i] {
                want = Some(i);
                break;
            }
            seen[i] = true;
            cur = next[i];
        }
        check!(format!("next = {next:?}, head = {head:?}"), (cycle_start(&next, head), has_cycle(&next, head)), (want, want.is_some()));
    }
}

#[test]
fn scale_200k() {
    let mut next: Vec<Option<usize>> = (1..=200_000).map(Some).collect();
    next[199_999] = Some(123_456);
    let mut straight = next.clone();
    straight[199_999] = None;
    check!("200000 nodes, last → 123456; and the same without the back link", (cycle_start(&next, Some(0)), cycle_start(&straight, Some(0))), (Some(123_456), None));
}

#[test]
fn big_loop() {
    let mut next: Vec<Option<usize>> = (1..=100_000).map(Some).collect();
    next[99_999] = Some(40_000);
    check!(r#"10⁵ nodes, last points to 40_000"#, cycle_start(&next, Some(0)), Some(40_000));
}

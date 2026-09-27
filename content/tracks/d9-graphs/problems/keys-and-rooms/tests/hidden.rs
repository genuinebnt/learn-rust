use solution::*;

#[test]
fn duplicate_keys() {
    check!(r#"rooms = [[1,1,1],[0,0]]"#, can_visit_all_rooms(&[vec![1, 1, 1], vec![0, 0]]), true);
}

#[test]
fn keys_to_room_zero_only() {
    check!(r#"rooms = [[0],[0],[0]]"#, can_visit_all_rooms(&[vec![0], vec![0], vec![0]]), false);
}

#[test]
fn keys_in_reverse() {
    check!(r#"rooms = [[3],[],[1],[2]]"#, can_visit_all_rooms(&[vec![3], vec![], vec![1], vec![2]]), true);
}

#[test]
fn star() {
    check!(r#"room 0 holds every key"#, can_visit_all_rooms(&[vec![4, 3, 2, 1], vec![], vec![], vec![], vec![]]), true);
}

#[test]
fn cycle_skips_a_room() {
    check!(r#"rooms = [[1],[2],[0],[]]"#, can_visit_all_rooms(&[vec![1], vec![2], vec![0], vec![]]), false);
}

#[test]
fn last_room_unreachable_in_a_big_house() {
    let n = 200_000;
    let rooms: Vec<Vec<usize>> = (0..n).map(|i| if i + 2 < n { vec![i + 1] } else { vec![] }).collect();
    check!(r#"200000 rooms, i holds key i + 1 except the second-to-last"#, can_visit_all_rooms(&rooms), false);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(940);
    for _ in 0..300 {
        let n = 1 + rng.below(7);
        let rooms: Vec<Vec<usize>> = (0..n).map(|_| { let k = rng.below(3); (0..k).map(|_| rng.below(n)).collect() }).collect();
        // Brute force: keep opening rooms whose key is in an open room until nothing changes.
        let mut open = vec![false; n];
        open[0] = true;
        let mut changed = true;
        while changed {
            changed = false;
            for i in 0..n {
                if open[i] {
                    for &k in &rooms[i] {
                        if !open[k] {
                            open[k] = true;
                            changed = true;
                        }
                    }
                }
            }
        }
        check!(format!("rooms = {rooms:?}"), can_visit_all_rooms(&rooms), open.iter().all(|&o| o));
    }
}

#[test]
fn scale_chain_200k() {
    // Room i holds the key to room i + 1, listed so room 0 is visited first.
    let n = 200_000;
    let rooms: Vec<Vec<usize>> = (0..n).map(|i| if i + 1 < n { vec![i + 1] } else { vec![] }).collect();
    check!("200000 rooms, room i holds key i + 1", can_visit_all_rooms(&rooms), true);
}

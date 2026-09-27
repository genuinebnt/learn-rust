use solution::*;

#[test]
fn rotate_empty() {
    check!(r#"v = [], k = 3"#, { let mut v: [i32; 0] = []; rotate_right(&mut v, 3); v }, []);
}

#[test]
fn rotate_large_k() {
    check!(r#"v = [1, 2, 3], k = 7"#, { let mut v = [1, 2, 3]; rotate_right(&mut v, 7); v }, [3, 1, 2]);
}

#[test]
fn rotate_k_max() {
    check!(r#"v = [1, 2, 3, 4, 5, 6, 7], k = usize::MAX (≡ 1 mod 7)"#, { let mut v = [1, 2, 3, 4, 5, 6, 7]; rotate_right(&mut v, usize::MAX); v }, [7, 1, 2, 3, 4, 5, 6]);
}

#[test]
fn rotate_full_turn() {
    check!(r#"v = [1, 2], k = 2"#, { let mut v = [1, 2]; rotate_right(&mut v, 2); v }, [1, 2]);
}

#[test]
fn move_same_index() {
    let mut v = ["a", "b", "c"];
    move_item(&mut v, 1, 1);
    check!(r#"v = ["a", "b", "c"], from = 1, to = 1"#, v, ["a", "b", "c"]);
}

#[test]
fn move_to_end() {
    let mut v = ["a", "b", "c"];
    move_item(&mut v, 0, 2);
    check!(r#"v = ["a", "b", "c"], from = 0, to = 2"#, v, ["b", "c", "a"]);
}

#[test]
fn move_adjacent_left() {
    let mut v = ["a", "b", "c"];
    move_item(&mut v, 2, 1);
    check!(r#"v = ["a", "b", "c"], from = 2, to = 1"#, v, ["a", "c", "b"]);
}

#[test]
fn move_from_out_of_range() {
    let mut v = ["a", "b"];
    move_item(&mut v, 2, 0);
    check!(r#"v = ["a", "b"], from = 2, to = 0"#, v, ["a", "b"]);
}

#[test]
fn move_to_out_of_range() {
    let mut v = ["a", "b"];
    move_item(&mut v, 0, 2);
    check!(r#"v = ["a", "b"], from = 0, to = 2"#, v, ["a", "b"]);
}

#[test]
fn move_only_touches_between() {
    let mut v: Vec<String> = (0..30).map(|i| i.to_string()).collect();
    let ptrs: Vec<*const u8> = v.iter().map(|s| s.as_ptr()).collect();
    move_item(&mut v, 5, 7);
    check!(r#"30 Strings, move 5 → 7: the rest keep their buffers"#, (v[..5].iter().zip(&ptrs[..5]).all(|(s, p)| s.as_ptr() == *p), v[8..].iter().zip(&ptrs[8..]).all(|(s, p)| s.as_ptr() == *p), v[7].as_str()), (true, true, "5"));
}

#[test]
fn swap_even_length() {
    check!(r#"v = [1, 2, 3, 4]"#, { let mut v = [1, 2, 3, 4]; swap_pairs(&mut v); v }, [2, 1, 4, 3]);
}

#[test]
fn swap_short() {
    check!(r#"v = [] and [7]"#, { let mut a: [i32; 0] = []; let mut b = [7]; swap_pairs(&mut a); swap_pairs(&mut b); (a, b) }, ([], [7]));
}

#[test]
fn swap_strings() {
    check!(r#"v = ["a", "b", "c"]"#, { let mut v = vec!["a".to_string(), "b".to_string(), "c".to_string()]; swap_pairs(&mut v); v }, vec!["b", "a", "c"]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7306);
    for _ in 0..400 {
        let n = rng.below(9);
        let v: Vec<i32> = (0..n as i32).collect();
        let k = rng.below(20);
        let want_rot: Vec<i32> = (0..n).map(|i| v[(i + n - k % n.max(1)) % n.max(1)]).collect();
        let (from, to) = (rng.below(n + 2), rng.below(n + 2));
        let mut want_move = v.clone();
        if from < n && to < n {
            let x = want_move.remove(from);
            want_move.insert(to, x);
        }
        let want_swap: Vec<i32> = (0..n).map(|i| if i % 2 == 0 && i + 1 < n { v[i + 1] } else if i % 2 == 1 { v[i - 1] } else { v[i] }).collect();
        let (mut a, mut b, mut c) = (v.clone(), v.clone(), v.clone());
        rotate_right(&mut a, k);
        move_item(&mut b, from, to);
        swap_pairs(&mut c);
        check!(format!("v = {v:?}, k = {k}, from = {from}, to = {to}"), (a, b, c), (want_rot, want_move, want_swap));
    }
}

#[test]
fn scale_200k() {
    let mut v: Vec<i32> = (0..200_000).collect();
    rotate_right(&mut v, 100_000);
    for i in 0..100_000 {
        move_item(&mut v, i, i + 1);
    }
    swap_pairs(&mut v);
    check!("v = 0..200000: rotate 100000, 100000 adjacent moves, swap pairs", (v[0], v[1], v[99_999], v[100_000], v[199_999]), (100_002, 100_001, 199_999, 1, 99_998));
}

use solution::*;

#[test]
fn remove_everything() {
    let mut v = vec![5, 6, 7];
    remove_indices(&mut v, &[2, 1, 0]);
    check!(r#"v = [5, 6, 7], indices = [2, 1, 0]"#, v, Vec::<i32>::new());
}

#[test]
fn all_out_of_range() {
    let mut v = vec![5, 6];
    remove_indices(&mut v, &[2, 7, 100]);
    check!(r#"v = [5, 6], indices = [2, 7, 100]"#, v, vec![5, 6]);
}

#[test]
fn empty_vec() {
    let mut v: Vec<i32> = vec![];
    remove_indices(&mut v, &[0, 1]);
    check!(r#"v = [], indices = [0, 1]"#, v, Vec::<i32>::new());
}

#[test]
fn first_and_last() {
    let mut v = vec![1, 2, 3, 4, 5];
    remove_indices(&mut v, &[4, 0]);
    check!(r#"v = [1, 2, 3, 4, 5], indices = [4, 0]"#, v, vec![2, 3, 4]);
}

#[test]
fn many_repeats() {
    let mut v = vec![1, 2, 3];
    remove_indices(&mut v, &[1, 1, 1, 1]);
    check!(r#"v = [1, 2, 3], indices = [1, 1, 1, 1]"#, v, vec![1, 3]);
}

#[test]
fn huge_index() {
    let mut v = vec![1, 2];
    remove_indices(&mut v, &[18446744073709551615]);
    check!(r#"v = [1, 2], indices = [18446744073709551615]"#, v, vec![1, 2]);
}

#[test]
fn unordered_everything() {
    let mut v: Vec<i32> = vec![1, 2, 3, 4];
    let removed = remove_indices_unordered(&mut v, &[0, 1, 2, 3]);
    check!(r#"v = [1, 2, 3, 4], indices = [0, 1, 2, 3]"#, (removed, v), (vec![4, 3, 2, 1], Vec::<i32>::new()));
}

#[test]
fn unordered_repeats_and_out_of_range() {
    let mut v: Vec<i32> = vec![1, 2, 3, 4, 5];
    let removed = remove_indices_unordered(&mut v, &[1, 1, 9, 4]);
    check!(r#"v = [1, 2, 3, 4, 5], indices = [1, 1, 9, 4]"#, (removed, v), (vec![5, 2], vec![1, 4, 3]));
}

#[test]
fn unordered_last_two() {
    let mut v: Vec<i32> = vec![1, 2, 3, 4];
    let removed = remove_indices_unordered(&mut v, &[3, 2]);
    check!(r#"v = [1, 2, 3, 4], indices = [3, 2]"#, (removed, v), (vec![4, 3], vec![1, 2]));
}

#[test]
fn unordered_nothing() {
    let mut v: Vec<i32> = vec![1, 2];
    let removed = remove_indices_unordered(&mut v, &[5]);
    check!(r#"v = [1, 2], indices = [5]"#, (removed, v), (Vec::<i32>::new(), vec![1, 2]));
}

#[test]
fn strings() {
    let words = vec!["a".to_string(), "b".to_string(), "c".to_string(), "d".to_string()];
    let (mut a, mut b) = (words.clone(), words);
    remove_indices(&mut a, &[0, 2]);
    let removed = remove_indices_unordered(&mut b, &[0, 2]);
    check!(r#"v = ["a", "b", "c", "d"], remove [0, 2] (both ways)"#, (a, b, removed), (["b", "d"].map(String::from).to_vec(), ["d", "b"].map(String::from).to_vec(), ["c", "a"].map(String::from).to_vec()));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7301);
    for _ in 0..400 {
        let n = rng.below(10);
        let v: Vec<i32> = (0..n as i32).collect();
        let k = rng.below(6);
        let idx: Vec<usize> = (0..k).map(|_| rng.below(n + 2)).collect();
        let want: Vec<i32> = v.iter().copied().filter(|&x| !idx.contains(&(x as usize))).collect();
        let mut sorted: Vec<usize> = idx.iter().copied().filter(|&i| i < n).collect();
        sorted.sort();
        sorted.dedup();
        let mut left = v.clone();
        let mut removed = Vec::new();
        for &i in sorted.iter().rev() {
            let last = left.len() - 1;
            left.swap(i, last);
            removed.push(left.pop().unwrap());
        }
        let (mut a, mut b) = (v.clone(), v.clone());
        remove_indices(&mut a, &idx);
        let got_removed = remove_indices_unordered(&mut b, &idx);
        check!(format!("v = {v:?}, indices = {idx:?}"), (a, got_removed, b), (want, removed, left));
    }
}

#[test]
fn scale_remove_100k_of_300k() {
    let mut v: Vec<u64> = (0..300_000).collect();
    let idx: Vec<usize> = (1..200_000).step_by(2).rev().collect();
    remove_indices(&mut v, &idx);
    check!("v = 0..300000, remove the odd indices below 200000 (listed high to low)", (v.len(), v[0], v[99_999], v[100_000]), (200_000, 0, 199_998, 200_000));
    let mut w: Vec<u64> = (0..300_000).collect();
    let removed = remove_indices_unordered(&mut w, &idx);
    check!("the same, unordered", (w.len(), removed.len(), removed[0]), (200_000, 100_000, 199_999));
}

use solution::*;

#[test]
fn zeros() {
    check!(r#"script([0, 0, 0])"#, { let mut v: Vec<i32> = vec![0, 0, 0]; let mut log = Vec::new(); script(&mut v, &mut log); (v, log) }, (vec![3, 3, 5, 5, 5, 3, 3], vec![3, 3]));
}

#[test]
fn two() {
    check!(r#"script([5, 5])"#, { let mut v: Vec<i32> = vec![5, 5]; let mut log = Vec::new(); script(&mut v, &mut log); (v, log) }, (vec![2, 2, 5, 5, 5, 2, 2], vec![4, 3]));
}

#[test]
fn six() {
    check!(r#"script([3, 1, 4, 1, 5, 9])"#, { let mut v: Vec<i32> = vec![3, 1, 4, 1, 5, 9]; let mut log = Vec::new(); script(&mut v, &mut log); (v, log) }, (vec![1, 4, 6, 1, 5, 9, 9, 9, 1, 4, 6, 1], vec![8, 8]));
}

#[test]
fn big_first() {
    check!(r#"script([100, 1, 2, 3, 4, 5, 6])"#, { let mut v: Vec<i32> = vec![100, 1, 2, 3, 4, 5, 6]; let mut log = Vec::new(); script(&mut v, &mut log); (v, log) }, (vec![2, 3, 7, 4, 5, 6, 6, 6, 2, 3, 7, 4], vec![8, 10]));
}

#[test]
fn all_negative() {
    check!(r#"script([-1, -2, -3, -4])"#, { let mut v: Vec<i32> = vec![-1, -2, -3, -4]; let mut log = Vec::new(); script(&mut v, &mut log); (v, log) }, (vec![-2, 4, 5, 5, 5, -2, 4], vec![4, 5]));
}

#[test]
fn mixed_eight() {
    check!(r#"script([2, 7, 1, 8, 2, 8, 1, 8])"#, { let mut v: Vec<i32> = vec![2, 7, 1, 8, 2, 8, 1, 8]; let mut log = Vec::new(); script(&mut v, &mut log); (v, log) }, (vec![1, 8, 8, 2, 8, 1, 8, 12, 12, 12, 1, 8, 8, 2, 8], vec![10, 12]));
}

#[test]
fn ten() {
    check!(r#"script([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])"#, { let mut v: Vec<i32> = vec![0, 1, 2, 3, 4, 5, 6, 7, 8, 9]; let mut log = Vec::new(); script(&mut v, &mut log); (v, log) }, (vec![3, 4, 10, 5, 6, 7, 8, 9, 9, 9, 3, 4, 10, 5, 6], vec![10, 13]));
}

#[test]
fn ten_desc() {
    check!(r#"script([10, 9, 8, 7, 6, 5, 4, 3, 2, 1])"#, { let mut v: Vec<i32> = vec![10, 9, 8, 7, 6, 5, 4, 3, 2, 1]; let mut log = Vec::new(); script(&mut v, &mut log); (v, log) }, (vec![7, 10, 22, 10, 9, 9, 9, 7, 10, 22], vec![6, 8]));
}

fn model(v: &mut Vec<i32>) -> Vec<usize> {
    let mut log = Vec::new();
    let n = v.len() as i32;
    v.push(n);
    let n = v.len();
    v.swap(0, n - 1);
    let (at, first) = (v.len() / 2, v[0]);
    v.insert(at, first);
    let n = v.len();
    v[n - 1] += n as i32;
    let last = v.pop().unwrap();
    v.insert(0, last);
    let n = v.len();
    v.rotate_left(n / 3);
    let first = v[0];
    v.retain(|&x| x >= first);
    log.push(v.len());
    let n = v.len();
    v.truncate(n - n / 4);
    let last = v[v.len() - 1];
    v.push(last);
    v.push(last);
    let half = v[..v.len() / 2].to_vec();
    v.extend(half);
    let first = v[0];
    log.push(v.iter().filter(|&&x| x > first).count());
    log
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6214);
    for _ in 0..400 {
        let n = rng.below(12);
        let start: Vec<i32> = rng.vec(n, -20, 20);
        let mut want = start.clone();
        let want_log = model(&mut want);
        let mut got = start.clone();
        let mut log = Vec::new();
        script(&mut got, &mut log);
        check!(format!("script({start:?})"), (got, log), (want, want_log));
    }
}

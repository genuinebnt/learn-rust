use solution::*;

#[test]
fn left_wins() {
    check!(r#"[1,-2,-2,-2]"#, asteroid_collision(&[1, -2, -2, -2]), vec![-2, -2, -2]);
}

#[test]
fn empty() {
    check!(r#"[]"#, asteroid_collision(&[]), Vec::<i32>::new());
}

#[test]
fn single() {
    check!(r#"[-3]"#, asteroid_collision(&[-3]), vec![-3]);
}

#[test]
fn all_right() {
    check!(r#"[1,2,3]"#, asteroid_collision(&[1, 2, 3]), vec![1, 2, 3]);
}

#[test]
fn all_left() {
    check!(r#"[-1,-2]"#, asteroid_collision(&[-1, -2]), vec![-1, -2]);
}

#[test]
fn equal_then_bigger() {
    check!(r#"[1,-1,-2]"#, asteroid_collision(&[1, -1, -2]), vec![-2]);
}

#[test]
fn wins_then_ties() {
    check!(r#"[2,-1,-2]"#, asteroid_collision(&[2, -1, -2]), Vec::<i32>::new());
}

#[test]
fn big_left_mover_ties() {
    check!(r#"[10,-5,-10]"#, asteroid_collision(&[10, -5, -10]), Vec::<i32>::new());
}

#[test]
fn extremes() {
    check!(r#"[i32::MAX, -i32::MAX]"#, asteroid_collision(&[i32::MAX, -i32::MAX]), Vec::<i32>::new());
}

#[test]
fn random_vs_simulation() {
    // Resolve any adjacent right-mover / left-mover pair until none is left.
    fn brute(a: &[i32]) -> Vec<i32> {
        let mut v = a.to_vec();
        while let Some(i) = (0..v.len().saturating_sub(1)).find(|&i| v[i] > 0 && v[i + 1] < 0) {
            let (l, r) = (v[i], -v[i + 1]);
            if l > r {
                v.remove(i + 1);
            } else if l < r {
                v.remove(i);
            } else {
                v.drain(i..i + 2);
            }
        }
        v
    }
    let mut rng = anneal_prelude::Rng::new(3008);
    for _ in 0..400 {
        let n = rng.below(10);
        let a: Vec<i32> = (0..n).map(|_| { let x = rng.int(-5, 4) as i32; if x >= 0 { x + 1 } else { x } }).collect();
        check!(format!("asteroids = {a:?}"), asteroid_collision(&a), brute(&a));
    }
}

#[test]
fn scale_one_big_left_mover() {
    let mut a = vec![-1; 100_000];
    a.extend(vec![1; 100_000]);
    a.push(-200_000);
    let out = asteroid_collision(&a);
    check!("100000 × -1, 100000 × 1, then -200000", (out.len(), out[0], out[100_000]), (100_001, -1, -200_000));
}

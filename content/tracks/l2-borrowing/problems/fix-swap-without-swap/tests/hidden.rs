use solution::*;

#[test]
fn swap_backwards() {
    check!(r#"["a", "b", "c"]; swap_items(2, 0)"#, { let mut v = ["a", "b", "c"].map(String::from); swap_items(&mut v, 2, 0); v }, ["c", "b", "a"].map(String::from));
}

#[test]
fn swap_adjacent() {
    check!(r#"["x", "y"]; swap_items(0, 1)"#, { let mut v = ["x", "y"].map(String::from); swap_items(&mut v, 0, 1); v }, ["y", "x"].map(String::from));
}

#[test]
fn swap_single() {
    check!(r#"["only"]; swap_items(0, 0)"#, { let mut v = ["only"].map(String::from); swap_items(&mut v, 0, 0); v }, ["only"].map(String::from));
}

#[test]
fn rotate3_reversed_indices() {
    check!(r#"["x", "y", "z"]; rotate3(2, 1, 0)"#, { let mut v = ["x", "y", "z"].map(String::from); rotate3(&mut v, 2, 1, 0); v }, ["z", "x", "y"].map(String::from));
}

#[test]
fn rotate3_spread() {
    check!(r#"["a", "b", "c", "d"]; rotate3(0, 3, 1)"#, { let mut v = ["a", "b", "c", "d"].map(String::from); rotate3(&mut v, 0, 3, 1); v }, ["d", "a", "c", "b"].map(String::from));
}

#[test]
fn append_empty() {
    check!(r#"["a", ""]; append_copy(0, 1)"#, { let mut v = ["a", ""].map(String::from); append_copy(&mut v, 0, 1); v }, ["a", ""].map(String::from));
}

#[test]
fn append_empty_self() {
    check!(r#"["a", ""]; append_copy(1, 1)"#, { let mut v = ["a", ""].map(String::from); append_copy(&mut v, 1, 1); v }, ["a", ""].map(String::from));
}

#[test]
fn append_unicode() {
    check!(r#"["日本", "-", "x"]; append_copy(2, 0)"#, { let mut v = ["日本", "-", "x"].map(String::from); append_copy(&mut v, 2, 0); v }, ["日本", "-", "x日本"].map(String::from));
}

#[test]
fn strings_moved_not_copied() {
    let mut v = ["first", "second"].map(String::from);
    let (p0, p1) = (v[0].as_ptr(), v[1].as_ptr());
    swap_items(&mut v, 0, 1);
    check!(r#"swap_items(0, 1) moves the Strings"#, (v[0].as_ptr() == p1, v[1].as_ptr() == p0), (true, true));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6227);
    for _ in 0..300 {
        let n = 3 + rng.below(3);
        let mut v: Vec<String> = Vec::new();
        for _ in 0..n {
            let len = 1 + rng_len(&mut rng);
            v.push(rng.string(len, "ab"));
        }
        let (i, j) = (rng.below(n), rng.below(n));
        let mut got = v.clone();
        swap_items(&mut got, i, j);
        let mut want = v.clone();
        want.swap(i, j);
        check!(format!("{v:?}; swap_items({i}, {j})"), got, want);
        let mut got = v.clone();
        append_copy(&mut got, i, j);
        let mut want = v.clone();
        let add = v[j].clone();
        want[i].push_str(&add);
        check!(format!("{v:?}; append_copy({i}, {j})"), got, want);
        let mut idx: Vec<usize> = (0..n).collect();
        rng.shuffle(&mut idx);
        let (a, b, c) = (idx[0], idx[1], idx[2]);
        let mut got = v.clone();
        rotate3(&mut got, a, b, c);
        let mut want = v.clone();
        want[a] = v[b].clone();
        want[b] = v[c].clone();
        want[c] = v[a].clone();
        check!(format!("{v:?}; rotate3({a}, {b}, {c})"), got, want);
    }
}

fn rng_len(rng: &mut anneal_prelude::Rng) -> usize {
    rng.below(3)
}

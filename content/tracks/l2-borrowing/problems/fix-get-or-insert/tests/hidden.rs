use solution::*;

#[test]
fn mut_then_shared() {
    let mut c = Cache::new();
    *c.get_or_make_mut(4, String::new) = "w".to_string();
    check!(r#"get_or_make_mut 4 = "w", get_or_make 4"#, c.get_or_make(4, || "no".to_string()).clone(), "w".to_string());
}

#[test]
fn mut_hit_keeps_value() {
    let mut c = Cache::new();
    c.get_or_make(6, || "k".to_string());
    check!(r#"get_or_make 6 ("k"), get_or_make_mut 6 ("no")"#, c.get_or_make_mut(6, || "no".to_string()).clone(), "k".to_string());
}

#[test]
fn mut_make_once() {
    let mut c = Cache::new();
    let mut calls = 0;
    c.get_or_make_mut(7, || { calls += 1; String::new() });
    c.get_or_make_mut(7, || { calls += 1; String::new() });
    check!(r#"get_or_make_mut 7 twice, counting make"#, calls, 1);
}

#[test]
fn misses_mixed() {
    let mut c = Cache::new();
    c.get_or_make(1, String::new);
    c.get_or_make(2, String::new);
    c.get_or_make_mut(2, String::new);
    c.get_or_make_mut(3, String::new);
    check!(r#"keys 1, 2 via get_or_make, 2, 3 via get_or_make_mut"#, (c.misses(), c.order().to_vec()), (3, vec![1, 2, 3]));
}

#[test]
fn key_zero_and_max() {
    let mut c = Cache::new();
    check!(r#"keys 0 and u32::MAX"#, (c.get_or_make(0, || "lo".to_string()).clone(), c.get_or_make(u32::MAX, || "hi".to_string()).clone()), ("lo".to_string(), "hi".to_string()));
}

#[test]
fn returned_value_is_stored() {
    let mut c = Cache::new();
    let p = c.get_or_make_mut(9, || "stored".to_string()).as_ptr();
    check!(r#"the &String from get_or_make_mut is the stored one"#, p == c.get_or_make(9, String::new).as_ptr(), true);
}

#[test]
fn new_cache() {
    let mut c = Cache::new();
    check!(r#"new cache"#, (c.misses(), c.order().len()), (0, 0));
}

#[test]
fn unicode_value() {
    let mut c = Cache::new();
    check!(r#"get_or_make 1 ("日本")"#, c.get_or_make(1, || "日本".to_string()).clone(), "日本".to_string());
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6230);
    for _ in 0..300 {
        let mut c = Cache::new();
        let mut model: Vec<(u32, String)> = Vec::new();
        let mut misses = 0;
        let mut ops = Vec::new();
        for step in 0..10 {
            let k = rng.below(4) as u32;
            let made = format!("v{step}");
            if model.iter().all(|e| e.0 != k) {
                misses += 1;
                model.push((k, made.clone()));
            }
            let want = model.iter().find(|e| e.0 == k).unwrap().1.clone();
            if rng.bool() {
                ops.push(format!("get_or_make({k})"));
                check!(ops.join(", "), c.get_or_make(k, || made).clone(), want);
            } else {
                ops.push(format!("get_or_make_mut({k}) += \"!\""));
                let v = c.get_or_make_mut(k, || made);
                check!(ops.join(", "), v.clone(), want);
                v.push('!');
                model.iter_mut().find(|e| e.0 == k).unwrap().1.push('!');
            }
        }
        let order: Vec<u32> = model.iter().map(|e| e.0).collect();
        check!(format!("{}; misses, order", ops.join(", ")), (c.misses(), c.order().to_vec()), (misses, order));
    }
}

#[test]
fn many_keys() {
    let mut c = Cache::new();
    for i in 0..200_000u32 {
        c.get_or_make(i % 50_000, || i.to_string());
    }
    check!("200000 lookups over 50000 keys", (c.misses(), c.get_or_make(49_999, String::new).clone()), (50_000, "49999".to_string()));
}

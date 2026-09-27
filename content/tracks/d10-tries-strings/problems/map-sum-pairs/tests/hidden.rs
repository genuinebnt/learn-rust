use solution::*;

#[test]
fn past_i32() {
    let mut m = MapSum::new();
    for k in ["ka", "kb", "kc"] {
        m.insert(k, i32::MAX);
    }
    check!(r#"insert 3 keys with i32::MAX; sum("k")"#, m.sum("k"), 3 * i64::from(i32::MAX));
}

#[test]
fn negatives() {
    let mut m = MapSum::new();
    m.insert("ab", -5);
    m.insert("abc", 2);
    check!(r#"insert("ab", -5), ("abc", 2); sum("ab")"#, m.sum("ab"), -3);
}

#[test]
fn overwrite_to_zero() {
    let mut m = MapSum::new();
    m.insert("x", 7);
    m.insert("x", 0);
    check!(r#"insert("x", 7); insert("x", 0); sum("x")"#, m.sum("x"), 0);
}

#[test]
fn overwrite_min_to_max() {
    let mut m = MapSum::new();
    m.insert("x", i32::MIN);
    m.insert("x", i32::MAX);
    check!(r#"insert("x", i32::MIN); insert("x", i32::MAX); sum("")"#, m.sum(""), i64::from(i32::MAX));
}

#[test]
fn overwrite_leaves_others() {
    let mut m = MapSum::new();
    m.insert("a", 1);
    m.insert("ab", 2);
    m.insert("a", 10);
    check!(r#"insert("a", 1), ("ab", 2), ("a", 10); sum("a"), sum("ab")"#, (m.sum("a"), m.sum("ab")), (12, 2));
}

#[test]
fn longer_prefix_than_key() {
    let mut m = MapSum::new();
    m.insert("ab", 4);
    check!(r#"insert("ab", 4); sum("abc")"#, m.sum("abc"), 0);
}

#[test]
fn sibling_keys() {
    let mut m = MapSum::new();
    m.insert("car", 1);
    m.insert("cat", 2);
    m.insert("cup", 4);
    check!(r#"insert("car", 1), ("cat", 2), ("cup", 4); sum("ca"), sum("c")"#, (m.sum("ca"), m.sum("c")), (3, 7));
}

#[test]
fn same_value_again() {
    let mut m = MapSum::new();
    m.insert("k", 5);
    m.insert("k", 5);
    check!(r#"insert("k", 5) twice; sum("k")"#, m.sum("k"), 5);
}

        #[test]
        fn random_vs_model() {
            use std::collections::HashMap;
            let mut rng = anneal_prelude::Rng::new(1005);
            for _ in 0..300 {
                let mut m = MapSum::new();
                let mut model: HashMap<String, i32> = HashMap::new();
                let mut log = Vec::new();
                for _ in 0..rng.below(12) {
                    let len = rng.below(4);
                    let key = rng.string(len, "ab");
                    if rng.bool() && !key.is_empty() {
                        let val = rng.int(-9, 9) as i32;
                        m.insert(&key, val);
                        log.push(format!("insert({key:?}, {val})"));
                        model.insert(key, val);
                    } else {
                        log.push(format!("sum({key:?})"));
                        let want: i64 = model.iter().filter(|(k, _)| k.starts_with(key.as_str())).map(|(_, &v)| i64::from(v)).sum();
                        check!(log.join(", "), m.sum(&key), want);
                    }
                }
            }
        }

        #[test]
        fn scale_100k_keys_and_sums() {
            let mut m = MapSum::new();
            for i in 0..100_000 {
                m.insert(&base10(i, 5), 1_000);
            }
            let mut total = 0i64;
            for i in 0..100_000 {
                total += m.sum(&base10(i % 10, 1)) + m.sum("");
            }
            check!("insert 100000 keys with value 1000; then 100000 × (sum of a one-letter prefix + sum(\"\"))", total, 100_000 * (10_000_000 + 100_000_000));
        }

fn base10(mut i: usize, len: usize) -> String {
    let mut w = vec![b'a'; len];
    for k in (0..len).rev() {
        w[k] = b'a' + (i % 10) as u8;
        i /= 10;
    }
    String::from_utf8(w).unwrap()
}

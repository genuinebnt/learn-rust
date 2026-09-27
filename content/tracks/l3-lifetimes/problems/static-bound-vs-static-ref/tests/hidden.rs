use solution::*;

#[test]
fn empty() {
    check!(r#"nothing stored"#, Stash::new().all::<i64>().len(), 0);
}

#[test]
fn types_are_exact() {
    let mut s = Stash::new();
    s.put(1u64);
    check!(r#"put 1u64; all::<u32>()"#, s.all::<u32>().len(), 0);
}

#[test]
fn string_vs_str() {
    let mut s = Stash::new();
    s.put(String::from("a"));
    s.put("b");
    check!(r#"put String "a", &str "b""#, (s.all::<String>().iter().map(|x| x.as_str()).collect::<Vec<_>>(), s.all::<&str>()), (vec!["a"], vec![&"b"]));
}

#[test]
fn box_is_its_own_type() {
    let mut s = Stash::new();
    s.put(Box::new(1i32));
    s.put(2i32);
    check!(r#"put Box<i32>(1), 2i32"#, (s.all::<Box<i32>>().len(), s.all::<i32>()), (1, vec![&2]));
}

#[test]
fn unit_values() {
    let mut s = Stash::new();
    s.put(());
    s.put(());
    s.put(1u8);
    check!(r#"put (), (), 1u8"#, s.all::<()>().len(), 2);
}

#[test]
fn nested_owned() {
    let mut s = Stash::new();
    s.put(vec![String::from("x")]);
    let v = s.all::<Vec<String>>();
    check!(r#"put vec![String "x"]"#, (v.len(), v[0].clone()), (1, vec![String::from("x")]));
}

#[test]
fn options() {
    let mut s = Stash::new();
    s.put(Some(1u8));
    s.put(None::<u8>);
    s.put(Some(2u16));
    check!(r#"put Some(1u8), None::<u8>, Some(2u16)"#, s.all::<Option<u8>>(), vec![&Some(1u8), &None]);
}

#[test]
fn many() {
    let mut s = Stash::new();
    for i in 0..10_000u32 {
        s.put(i);
        s.put(u64::from(i));
    }
    let v = s.all::<u32>();
    check!(r#"10000 u32 values and 10000 u64 values interleaved"#, (v.len(), *v[0], *v[9_999]), (10_000, 0, 9_999));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(313);
    for _ in 0..300 {
        let n = rng.below(10);
        let mut s = Stash::new();
        let mut small: Vec<u8> = Vec::new();
        let mut wide: Vec<u16> = Vec::new();
        for _ in 0..n {
            let v = rng.int(0, 255);
            if rng.bool() {
                s.put(v as u8);
                small.push(v as u8);
            } else {
                s.put(v as u16);
                wide.push(v as u16);
            }
        }
        check!(format!("u8 values {small:?} and u16 values {wide:?}"), (s.all::<u8>(), s.all::<u16>()), (small.iter().collect::<Vec<_>>(), wide.iter().collect::<Vec<_>>()));
    }
}

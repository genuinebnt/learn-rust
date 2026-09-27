use solution::*;

#[test]
fn empty() {
    let mut ext = Extensions::new();
    check!(r#"new map"#, (ext.len(), ext.get::<u32>().is_none(), ext.remove::<u32>()), (0, true, None));
}

#[test]
fn distinct_integer_types() {
    let mut ext = Extensions::new();
    ext.insert(1u32);
    ext.insert(1u64);
    ext.insert(1i32);
    check!(r#"insert 1u32, 1u64, 1i32"#, ext.len(), 3);
}

#[test]
fn str_vs_string() {
    let mut ext = Extensions::new();
    ext.insert("a");
    ext.insert("b".to_string());
    check!(r#"insert "a" (&'static str) and "b" (String)"#, (ext.get::<&str>().copied(), ext.get::<String>().cloned()), (Some("a"), Some("b".to_string())));
}

#[test]
fn replace_keeps_len() {
    let mut ext = Extensions::new();
    check!(r#"insert 1u32 three times"#, { ext.insert(1u32); ext.insert(2u32); (ext.insert(3u32), ext.len()) }, (Some(2), 1));
}

#[test]
fn unit_type() {
    let mut ext = Extensions::new();
    check!(r#"insert ()"#, (ext.insert(()), ext.get::<()>().is_some()), (None, true));
}

#[test]
fn struct_value() {
    #[derive(Debug)]
    struct P(u8);
    let mut ext = Extensions::new();
    ext.insert(P(7));
    check!(r#"insert a local struct type"#, ext.get::<P>().map(|p| p.0), Some(7));
}

#[test]
fn get_mut_missing() {
    let mut ext = Extensions::new();
    check!(r#"get_mut::<u8> on an empty map"#, ext.get_mut::<u8>().is_none(), true);
}

#[test]
fn remember_order() {
    let mut log: Vec<Box<dyn std::fmt::Debug>> = Vec::new();
    remember(&mut log, 1);
    remember(&mut log, 2.5);
    remember(&mut log, 'c');
    check!(r#"remember 1, 2.5, 'c'"#, format!("{log:?}"), "[1, 2.5, 'c']");
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6310);
    for _ in 0..300 {
        let mut ext = Extensions::new();
        let (mut a, mut b): (Option<u32>, Option<String>) = (None, None);
        let mut ops = Vec::new();
        for _ in 0..8 {
            let x = rng.below(100) as u32;
            match rng.below(4) {
                0 => {
                    ops.push(format!("insert {x}u32"));
                    check!(ops.join(", "), ext.insert(x), a.replace(x));
                }
                1 => {
                    ops.push(format!("insert \"{x}\""));
                    check!(ops.join(", "), ext.insert(x.to_string()), b.replace(x.to_string()));
                }
                2 => {
                    ops.push("remove::<u32>".to_string());
                    check!(ops.join(", "), ext.remove::<u32>(), a.take());
                }
                _ => {
                    if let Some(v) = ext.get_mut::<String>() {
                        v.push('!');
                    }
                    if let Some(v) = b.as_mut() {
                        v.push('!');
                    }
                    ops.push("get_mut::<String> += !".to_string());
                }
            }
        }
        check!(format!("{}; state", ops.join(", ")), (ext.get::<u32>().copied(), ext.get::<String>().cloned(), ext.len()), (a, b.clone(), a.is_some() as usize + b.is_some() as usize));
    }
}

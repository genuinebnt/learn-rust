use solution::*;

#[test]
fn empty() {
    check!(r#"[]"#, parse_all(&[]), Ok(vec![]));
}

#[test]
fn overflow() {
    check!(r#"["99999999999"]"#, parse_all(&["99999999999"]), Err("bad number: 99999999999".to_string()));
}

#[test]
fn bounds() {
    check!(r#"["-2147483648", "2147483647"]"#, parse_all(&["-2147483648", "2147483647"]), Ok(vec![i32::MIN, i32::MAX]));
}

#[test]
fn just_past_max() {
    check!(r#"["2147483648"]"#, parse_all(&["2147483648"]), Err("bad number: 2147483648".to_string()));
}

#[test]
fn spaces_are_bad() {
    check!(r#"["1", " 2"]"#, parse_all(&["1", " 2"]), Err("bad number:  2".to_string()));
}

#[test]
fn last_is_bad() {
    check!(r#"["1", "2", "3.5"]"#, parse_all(&["1", "2", "3.5"]), Err("bad number: 3.5".to_string()));
}

#[test]
fn order_and_duplicates_kept() {
    check!(r#"["3", "1", "3"]"#, parse_all(&["3", "1", "3"]), Ok(vec![3, 1, 3]));
}

#[test]
fn unicode_item() {
    check!(r#"["7", "٣"]"#, parse_all(&["7", "٣"]), Err("bad number: ٣".to_string()));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1307);
    for _ in 0..400 {
        let n = rng.below(6);
        let mut items: Vec<String> = Vec::new();
        for _ in 0..n {
            if rng.below(5) == 0 {
                let len = rng.below(3);
                items.push(rng.string(len, "x1-"));
            } else {
                items.push(rng.int(-99, 99).to_string());
            }
        }
        let refs: Vec<&str> = items.iter().map(|s| s.as_str()).collect();
        let mut want: Result<Vec<i32>, String> = Ok(Vec::new());
        for s in &refs {
            match s.parse::<i32>() {
                Ok(v) => {
                    if let Ok(out) = &mut want {
                        out.push(v);
                    }
                }
                Err(_) => {
                    want = Err(format!("bad number: {s}"));
                    break;
                }
            }
        }
        check!(format!("items = {refs:?}"), parse_all(&refs), want);
    }
}

#[test]
fn scale_bad_item_at_the_end() {
    let mut items: Vec<String> = (0..200_000).map(|i: i32| (i - 100_000).to_string()).collect();
    let refs: Vec<&str> = items.iter().map(|s| s.as_str()).collect();
    let want: Vec<i32> = (0..200_000).map(|i| i - 100_000).collect();
    check!("200000 numbers from -100000 up", parse_all(&refs), Ok(want));
    items.push("oops".to_string());
    let refs: Vec<&str> = items.iter().map(|s| s.as_str()).collect();
    check!("the same 200000 numbers, then \"oops\"", parse_all(&refs), Err("bad number: oops".to_string()));
}

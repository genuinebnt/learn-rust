use solution::*;

/// A FromStr type whose error is a plain String (not an Error).
#[derive(Debug, PartialEq)]
struct Even(u32);

impl std::str::FromStr for Even {
    type Err = String;
    fn from_str(s: &str) -> Result<Even, String> {
        match s.parse::<u32>() {
            Ok(n) if n % 2 == 0 => Ok(Even(n)),
            _ => Err(format!("{s:?} is not even")),
        }
    }
}

#[test]
fn single() {
    check!(r#"parse_list::<u64>("18446744073709551615")"#, parse_list::<u64>("18446744073709551615"), Ok(vec![u64::MAX]));
}

#[test]
fn overflow() {
    check!(r#"parse_list::<u8>("1,256")"#, parse_list::<u8>("1,256").map_err(|e| e.to_string()), Err("item 1: number too large to fit in target type".to_string()));
}

#[test]
fn empty_item() {
    check!(r#"parse_list::<i32>("1,,2")"#, parse_list::<i32>("1,,2").map_err(|e| e.to_string()), Err("item 1: cannot parse integer from empty string".to_string()));
}

#[test]
fn first_bad_wins() {
    check!(r#"parse_list::<i32>("a,b")"#, parse_list::<i32>("a,b").map_err(|e| e.to_string()), Err("item 0: invalid digit found in string".to_string()));
}

#[test]
fn strings_never_fail() {
    check!(r#"parse_list::<String>(" a , b ")"#, parse_list::<String>(" a , b "), Ok(vec!["a".to_string(), "b".to_string()]));
}

#[test]
fn chars() {
    check!(r#"parse_list::<char>("é, x")"#, parse_list::<char>("é, x"), Ok(vec!['é', 'x']));
}

#[test]
fn empty_string() {
    check!(r#"parse_list::<i32>("")"#, parse_list::<i32>(""), Err(ParseListError::Empty));
}

#[test]
fn even_ok() {
    check!(r#"parse_list::<Even>("0,4")"#, parse_list::<Even>("0,4"), Ok(vec![Even(0), Even(4)]));
}

#[test]
fn empty_has_no_source() {
    use std::error::Error;
    check!(r#"parse_list::<i32>(" ").source()"#, parse_list::<i32>(" ").unwrap_err().source().is_none(), true);
}

#[test]
fn source_is_the_item_error() {
    use std::error::Error;
    check!(r#"parse_list::<std::net::Ipv4Addr>("1.2.3.4, 1.2.3")"#, parse_list::<std::net::Ipv4Addr>("1.2.3.4, 1.2.3").unwrap_err().source().map(|s| s.to_string()), Some("invalid IPv4 address syntax".to_string()));
}

#[test]
fn inferred_without_turbofish() {
    let v: Vec<u16> = parse_list("7, 8").unwrap();
    check!(r#"let v: Vec<u16> = parse_list("7, 8")?"#, v, vec![7u16, 8]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4503);
    for _ in 0..300 {
        let n = 1 + rng.below(4);
        let items: Vec<String> = (0..n).map(|_| if rng.below(5) == 0 { "x".to_string() } else { rng.int(-50, 50).to_string() }).collect();
        let s = items.join(" ,");
        let want = match items.iter().position(|x| x == "x") {
            Some(i) => Err(format!("item {i}: invalid digit found in string")),
            None => Ok(items.iter().map(|x| x.parse::<i8>().unwrap()).collect::<Vec<i8>>()),
        };
        check!(format!("s = {s:?}"), parse_list::<i8>(&s).map_err(|e| e.to_string()), want);
    }
}

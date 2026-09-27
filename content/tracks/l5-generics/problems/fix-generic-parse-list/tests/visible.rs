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
fn integers() {
    check!(r#"parse_list::<i32>("1, 2,3")"#, parse_list::<i32>("1, 2,3"), Ok(vec![1, 2, 3]));
}

#[test]
fn floats() {
    check!(r#"parse_list::<f64>(" 0.5 ,-2")"#, parse_list::<f64>(" 0.5 ,-2"), Ok(vec![0.5, -2.0]));
}

#[test]
fn bad_bool() {
    check!(r#"parse_list::<bool>("true, yes")"#, parse_list::<bool>("true, yes"), Err(ParseListError::Bad { index: 1, source: "yes".parse::<bool>().unwrap_err() }));
}

#[test]
fn empty() {
    check!(r#"parse_list::<u8>("  ")"#, parse_list::<u8>("  "), Err(ParseListError::Empty));
}

#[test]
fn error_that_is_not_an_error() {
    check!(r#"parse_list::<Even>("2, 3"): E = String"#, parse_list::<Even>("2, 3").map_err(|e| e.to_string()), Err("item 1: \"3\" is not even".to_string()));
}

#[test]
fn question_mark_into_box_dyn_error() {
    use std::error::Error;
    fn run() -> Result<i64, Box<dyn Error>> {
        Ok(parse_list::<i64>("4, x")?.iter().sum())
    }
    check!(r#"sum parse_list::<i64>("4, x") through ?"#, run().map_err(|e| (e.to_string(), e.source().map(|s| s.to_string()))), Err(("item 1: invalid digit found in string".to_string(), Some("invalid digit found in string".to_string()))));
}

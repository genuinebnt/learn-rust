use solution::*;

#[test]
fn empty_key() {
    check!(r#"" = 3""#, " = 3".parse::<Setting>(), Err(SettingError::EmptyKey));
}

#[test]
fn bad_value() {
    check!(r#""a = x ""#, "a = x ".parse::<Setting>(), Err(SettingError::BadValue("x".to_string())));
}

#[test]
fn second_equals_is_value() {
    check!(r#""a=b=c""#, "a=b=c".parse::<Setting>(), Err(SettingError::BadValue("b=c".to_string())));
}

#[test]
fn negative() {
    check!(r#""offset=-7""#, "offset=-7".parse::<Setting>(), Ok(Setting { key: "offset".to_string(), value: -7 }));
}

#[test]
fn empty_line() {
    check!(r#""""#, "".parse::<Setting>(), Err(SettingError::MissingEquals));
}

#[test]
fn just_equals() {
    check!(r#""=""#, "=".parse::<Setting>(), Err(SettingError::EmptyKey));
}

#[test]
fn missing_value() {
    check!(r#""a =""#, "a =".parse::<Setting>(), Err(SettingError::BadValue(String::new())));
}

#[test]
fn key_checked_first() {
    check!(r#"" = x""#, " = x".parse::<Setting>(), Err(SettingError::EmptyKey));
}

#[test]
fn key_with_space() {
    check!(r#""max retries = 2""#, "max retries = 2".parse::<Setting>(), Ok(Setting { key: "max retries".to_string(), value: 2 }));
}

#[test]
fn plus_sign() {
    check!(r#""a=+5""#, "a=+5".parse::<Setting>(), Ok(Setting { key: "a".to_string(), value: 5 }));
}

#[test]
fn i64_min() {
    check!(r#""a=-9223372036854775808""#, "a=-9223372036854775808".parse::<Setting>(), Ok(Setting { key: "a".to_string(), value: i64::MIN }));
}

#[test]
fn too_big() {
    check!(r#""a = 9223372036854775808""#, "a = 9223372036854775808".parse::<Setting>(), Err(SettingError::BadValue("9223372036854775808".to_string())));
}

#[test]
fn unicode_key_and_tabs() {
    check!(r#""délai\t=\t5""#, "délai\t=\t5".parse::<Setting>(), Ok(Setting { key: "délai".to_string(), value: 5 }));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2214);
    let keys = ["", "k", " k ", "a b", "é"];
    let values = ["1", " -2 ", "x", "", "3=4", "+0"];
    for _ in 0..300 {
        let key = *rng.pick(&keys);
        let value = *rng.pick(&values);
        let line = if rng.below(5) == 0 { format!("{key}{value}") } else { format!("{key}={value}") };
        let want = match line.find('=') {
            None => Err(SettingError::MissingEquals),
            Some(i) => {
                let (k, v) = (line[..i].trim(), line[i + 1..].trim());
                if k.is_empty() {
                    Err(SettingError::EmptyKey)
                } else {
                    match v.parse::<i64>() {
                        Ok(value) => Ok(Setting { key: k.to_string(), value }),
                        Err(_) => Err(SettingError::BadValue(v.to_string())),
                    }
                }
            }
        };
        check!(format!("line = {line:?}"), line.parse::<Setting>(), want);
    }
}

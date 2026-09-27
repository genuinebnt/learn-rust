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

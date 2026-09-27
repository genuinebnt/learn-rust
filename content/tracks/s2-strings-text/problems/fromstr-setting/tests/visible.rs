use solution::*;

#[test]
fn parses() {
    check!(r#""retries = 3""#, "retries = 3".parse::<Setting>(), Ok(Setting { key: "retries".to_string(), value: 3 }));
}

#[test]
fn no_equals() {
    check!(r#""retries""#, "retries".parse::<Setting>(), Err(SettingError::MissingEquals));
}

#[test]
fn spaces_trimmed() {
    check!(r#""  a   =   1  ""#, "  a   =   1  ".parse::<Setting>(), Ok(Setting { key: "a".to_string(), value: 1 }));
}

#[test]
fn bad_value_text() {
    check!(r#""x = ten""#, "x = ten".parse::<Setting>(), Err(SettingError::BadValue("ten".to_string())));
}

#[test]
fn empty_key_visible() {
    check!(r#""= 3""#, "= 3".parse::<Setting>(), Err(SettingError::EmptyKey));
}

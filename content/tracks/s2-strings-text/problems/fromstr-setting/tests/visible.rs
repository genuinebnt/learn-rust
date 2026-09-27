use solution::*;

#[test]
fn parses() {
    check!(r#""retries = 3""#, "retries = 3".parse::<Setting>(), Ok(Setting { key: "retries".to_string(), value: 3 }));
}

#[test]
fn no_equals() {
    check!(r#""retries""#, "retries".parse::<Setting>(), Err(SettingError::MissingEquals));
}

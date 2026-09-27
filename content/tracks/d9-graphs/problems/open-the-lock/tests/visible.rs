use solution::*;

#[test]
fn around_the_deadends() {
    check!(r#"deadends = ["0201","0101","0102","1212","2002"], target = "0202""#, open_lock(&["0201", "0101", "0102", "1212", "2002"], "0202"), Some(6));
}

#[test]
fn one_turn_down_wraps() {
    check!(r#"deadends = ["8888"], target = "0009""#, open_lock(&["8888"], "0009"), Some(1));
}

#[test]
fn target_boxed_in() {
    check!(r#"deadends = ["8887","8889","8878","8898","8788","8988","7888","9888"], target = "8888""#, open_lock(&["8887", "8889", "8878", "8898", "8788", "8988", "7888", "9888"], "8888"), None);
}

#[test]
fn already_open() {
    check!(r#"deadends = [], target = "0000""#, open_lock(&[], "0000"), Some(0));
}

#[test]
fn start_is_a_deadend() {
    check!(r#"deadends = ["0000"], target = "8888""#, open_lock(&["0000"], "8888"), None);
}

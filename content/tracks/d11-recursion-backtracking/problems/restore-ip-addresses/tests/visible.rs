use solution::*;

fn sorted<T: Ord>(mut v: Vec<T>) -> Vec<T> {
    v.sort();
    v
}

#[test]
fn leetcode_two_answers() {
    check!(r#"s = "25525511135""#, sorted(restore_ip_addresses("25525511135")), vec!["255.255.11.135", "255.255.111.35"]);
}

#[test]
fn leetcode_zeros() {
    check!(r#"s = "0000""#, restore_ip_addresses("0000"), vec!["0.0.0.0"]);
}

#[test]
fn leetcode_five_answers() {
    check!(r#"s = "101023""#, sorted(restore_ip_addresses("101023")), vec!["1.0.10.23", "1.0.102.3", "10.1.0.23", "10.10.2.3", "101.0.2.3"]);
}

#[test]
fn too_short() {
    check!(r#"s = "123""#, restore_ip_addresses("123"), Vec::<String>::new());
}

#[test]
fn no_leading_zeros() {
    check!(r#"s = "010010""#, sorted(restore_ip_addresses("010010")), vec!["0.10.0.10", "0.100.1.0"]);
}

use solution::*;

#[test]
fn typing_m() {
    let products = ["mobile", "mouse", "moneypot", "monitor", "mousepad"];
    check!(r#"products = ["mobile", "mouse", "moneypot", "monitor", "mousepad"], search_word = "m""#, suggested_products(&products, "m"), vec![vec!["mobile", "moneypot", "monitor"]]);
}

#[test]
fn typing_mo() {
    let products = ["mobile", "mouse", "moneypot", "monitor", "mousepad"];
    check!(r#"products = ["mobile", "mouse", "moneypot", "monitor", "mousepad"], search_word = "mo" (one list per letter typed)"#, suggested_products(&products, "mo"), vec![vec!["mobile", "moneypot", "monitor"], vec!["mobile", "moneypot", "monitor"]]);
}

#[test]
fn typing_mou() {
    let products = ["mobile", "mouse", "moneypot", "monitor", "mousepad"];
    check!(r#"products = ["mobile", "mouse", "moneypot", "monitor", "mousepad"], search_word = "mou" ("mou" narrows to two)"#, suggested_products(&products, "mou"), vec![vec!["mobile", "moneypot", "monitor"], vec!["mobile", "moneypot", "monitor"], vec!["mouse", "mousepad"]]);
}

#[test]
fn leetcode_mouse() {
    check!(r#"products = ["mobile", "mouse", "moneypot", "monitor", "mousepad"], search_word = "mouse""#, suggested_products(&["mobile", "mouse", "moneypot", "monitor", "mousepad"], "mouse"), vec![vec!["mobile", "moneypot", "monitor"], vec!["mobile", "moneypot", "monitor"], vec!["mouse", "mousepad"], vec!["mouse", "mousepad"], vec!["mouse", "mousepad"]]);
}

#[test]
fn leetcode_havana() {
    check!(r#"products = ["havana"], search_word = "havana""#, suggested_products(&["havana"], "havana"), vec![vec!["havana"]; 6]);
}

#[test]
fn leetcode_bags() {
    check!(r#"products = ["bags", "baggage", "banner", "box", "cloths"], search_word = "bags""#, suggested_products(&["bags", "baggage", "banner", "box", "cloths"], "bags"), vec![vec!["baggage", "bags", "banner"], vec!["baggage", "bags", "banner"], vec!["baggage", "bags"], vec!["bags"]]);
}

#[test]
fn miss_stays_empty() {
    check!(r#"products = ["havana"], search_word = "hat" ("hat" matches nothing, so the third list is empty)"#, suggested_products(&["havana"], "hat"), vec![vec!["havana"], vec!["havana"], vec![]]);
}

#[test]
fn empty_search_word() {
    check!(r#"products = ["a"], search_word = """#, suggested_products(&["a"], ""), Vec::<Vec<&str>>::new());
}

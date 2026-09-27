use solution::*;

#[test]
fn same_size_as_string() {
    check!(r#"size_of::<SmallStr>(), size_of::<Option<SmallStr>>()"#, (std::mem::size_of::<SmallStr>(), std::mem::size_of::<Option<SmallStr>>()), (24, 24));
}

#[test]
fn short_is_inline() {
    let (s, n) = anneal_prelude::allocs(|| SmallStr::new("DE"));
    check!(r#"SmallStr::new("DE")"#, (s.as_str(), s.is_inline(), n.count), ("DE", true, 0));
}

#[test]
fn long_goes_to_heap() {
    let (s, n) = anneal_prelude::allocs(|| SmallStr::new("payments-service-eu-west-1"));
    check!(r#"SmallStr::new("payments-service-eu-west-1") (26 bytes)"#, (s.as_str(), s.is_inline(), n.count, n.bytes), ("payments-service-eu-west-1", false, 1, 26));
}

#[test]
fn lookup_by_str() {
    let words = ["DE", "US", "a-much-longer-country-name"];
    let hashed: std::collections::HashSet<SmallStr> = words.iter().map(|&w| SmallStr::new(w)).collect();
    let sorted: std::collections::BTreeSet<SmallStr> = words.iter().map(|&w| SmallStr::new(w)).collect();
    check!(r#"HashSet and BTreeSet of SmallStr: contains("DE"), contains("FR")"#, (hashed.contains("DE"), hashed.contains("FR"), sorted.contains("DE"), sorted.contains("a-much-longer-country-name")), (true, false, true, true));
}

#[test]
fn prints_like_str() {
    let s = SmallStr::new("say \"hi\"");
    check!(r#"format!("{:?} {}") of SmallStr::new("say \"hi\"")"#, format!("{:?} {}", s, s), "\"say \\\"hi\\\"\" say \"hi\"");
}

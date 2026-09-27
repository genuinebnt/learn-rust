use solution::*;

fn sorted<T: Ord>(mut v: Vec<T>) -> Vec<T> {
    v.sort();
    v
}

#[test]
fn ones() {
    check!(r#"s = "1111""#, restore_ip_addresses("1111"), vec!["1.1.1.1"]);
}

#[test]
fn all_255() {
    check!(r#"s = "255255255255""#, restore_ip_addresses("255255255255"), vec!["255.255.255.255"]);
}

#[test]
fn part_256_is_too_big() {
    check!(r#"s = "256256256256""#, restore_ip_addresses("256256256256"), Vec::<String>::new());
}

#[test]
fn thirteen_digits() {
    check!(r#"s = "1231231231234""#, restore_ip_addresses("1231231231234"), Vec::<String>::new());
}

#[test]
fn twenty_digits() {
    check!(r#"s = 20 digits"#, restore_ip_addresses("12345678901234567890"), Vec::<String>::new());
}

#[test]
fn zero_then_256() {
    check!(r#"s = "000256""#, restore_ip_addresses("000256"), Vec::<String>::new());
}

#[test]
fn home_router() {
    check!(r#"s = "19216811""#, sorted(restore_ip_addresses("19216811")), vec!["1.92.168.11", "19.2.168.11", "19.21.68.11", "19.216.8.11", "19.216.81.1", "192.1.68.11", "192.16.8.11", "192.16.81.1", "192.168.1.1"]);
}

#[test]
fn five_ones() {
    check!(r#"s = "11111""#, sorted(restore_ip_addresses("11111")), vec!["1.1.1.11", "1.1.11.1", "1.11.1.1", "11.1.1.1"]);
}

#[test]
fn hundreds() {
    check!(r#"s = "100100""#, sorted(restore_ip_addresses("100100")), vec!["1.0.0.100", "10.0.10.0", "100.1.0.0"]);
}

#[test]
fn single_digit() {
    check!(r#"s = "5""#, restore_ip_addresses("5"), Vec::<String>::new());
}

#[test]
fn random_vs_three_cut_points() {
    let valid = |p: &str| !p.is_empty() && p.len() <= 3 && (p == "0" || !p.starts_with('0')) && p.parse::<u32>().unwrap() <= 255;
    let mut rng = anneal_prelude::Rng::new(1131);
    for _ in 0..400 {
        let n = rng.int(1, 13) as usize;
        let digits = *rng.pick(&["0125", "0123456789", "12", "0"]);
        let s = rng.string(n, digits);
        let mut want = Vec::new();
        for i in 1..n {
            for j in i + 1..n {
                for k in j + 1..n {
                    let parts = [&s[..i], &s[i..j], &s[j..k], &s[k..]];
                    if parts.iter().all(|p| valid(p)) {
                        want.push(parts.join("."));
                    }
                }
            }
        }
        want.sort();
        check!(format!("s = {s:?}"), sorted(restore_ip_addresses(&s)), want);
    }
}

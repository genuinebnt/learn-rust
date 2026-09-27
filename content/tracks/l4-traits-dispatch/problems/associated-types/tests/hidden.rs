use solution::*;

#[test]
fn csv_bad_part_fails() {
    check!(r#"CsvInts.decode("1,,2")"#, CsvInts.decode("1,,2"), None);
}

#[test]
fn csv_blank() {
    check!(r#"CsvInts.decode("   ")"#, CsvInts.decode("   "), Some(vec![]));
}

#[test]
fn csv_negative() {
    check!(r#"CsvInts.decode("-5, 7")"#, CsvInts.decode("-5, 7"), Some(vec![-5, 7]));
}

#[test]
fn csv_overflow_fails() {
    check!(r#"CsvInts.decode("99999999999999999999")"#, CsvInts.decode("99999999999999999999"), None);
}

#[test]
fn kv_no_equals() {
    check!(r#"KeyValue.decode("abc")"#, KeyValue.decode("abc"), None);
}

#[test]
fn kv_empty_sides() {
    check!(r#"KeyValue.decode("=")"#, KeyValue.decode("="), Some((String::new(), String::new())));
}

#[test]
fn names() {
    check!(r#"CsvInts::NAME, KeyValue::NAME"#, (<CsvInts as Decoder>::NAME, <KeyValue as Decoder>::NAME), ("csv", "kv"));
}

#[test]
fn first_decoded_kv() {
    check!(r#"first_decoded(&KeyValue, ["k=v"])"#, first_decoded(&KeyValue, &["k=v"]), r#"kv: ("k", "v")"#);
}

#[test]
fn first_decoded_empty() {
    check!(r#"first_decoded(&CsvInts, [])"#, first_decoded(&CsvInts, &[]), "csv: none");
}

#[test]
fn convert_by_annotation() {
    let f: Fahrenheit = Celsius(-40.0).convert();
    check!(r#"let f: Fahrenheit = Celsius(-40.0).convert()"#, format!("{:.2}", f.0), "-40.00");
}

#[test]
fn absolute_zero() {
    check!(r#"<Celsius as Convert<Kelvin>>::convert(&Celsius(-273.15))"#, format!("{:.2}", <Celsius as Convert<Kelvin>>::convert(&Celsius(-273.15)).0), "0.00");
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4404);
    for _ in 0..300 {
        let n = rng.below(4);
        let parts: Vec<String> = (0..n).map(|_| if rng.below(8) == 0 { "x".to_string() } else { rng.int(-99, 99).to_string() }).collect();
        let input = parts.join(",");
        let want: Option<Vec<i64>> = if input.is_empty() { Some(vec![]) } else { parts.iter().map(|p| p.parse().ok()).collect() };
        check!(format!("CsvInts.decode({input:?})"), CsvInts.decode(&input), want);
        let c = rng.int(-500, 500) as f64 / 2.0;
        let (f, k) = to_both(&Celsius(c));
        check!(format!("to_both(&Celsius({c}))"), format!("{:.3} {:.3}", f.0, k.0), format!("{:.3} {:.3}", c * 1.8 + 32.0, c + 273.15));
    }
}

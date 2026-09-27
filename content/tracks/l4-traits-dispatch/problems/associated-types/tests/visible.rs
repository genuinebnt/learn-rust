use solution::*;

#[test]
fn decode_csv() {
    check!(r#"decode_all(&CsvInts, ["1, 2", "x", ""])"#, decode_all(&CsvInts, &["1, 2", "x", ""]), vec![vec![1, 2], vec![]]);
}

#[test]
fn decode_kv() {
    check!(r#"KeyValue.decode(" a = b=c ")"#, KeyValue.decode(" a = b=c "), Some(("a".to_string(), "b=c".to_string())));
}

#[test]
fn first_decoded_csv() {
    check!(r#"first_decoded(&CsvInts, ["x", "3,4"])"#, first_decoded(&CsvInts, &["x", "3,4"]), "csv: [3, 4]");
}

#[test]
fn both_scales() {
    let (f, k) = to_both(&Celsius(100.0));
    check!(r#"to_both(&Celsius(100.0))"#, format!("{:.2} {:.2}", f.0, k.0), "212.00 373.15");
}

#[test]
fn a_new_decoder() {
    struct Flag;
    impl Decoder for Flag {
        type Output = bool;
        const NAME: &'static str = "flag";
        fn decode(&self, input: &str) -> Option<bool> {
            match input {
                "on" => Some(true),
                "off" => Some(false),
                _ => None,
            }
        }
    }
    check!("decode_all(&Flag, [\"on\", \"?\", \"off\"])", decode_all(&Flag, &["on", "?", "off"]), vec![true, false]);
    check!("first_decoded(&Flag, [\"?\"])", first_decoded(&Flag, &["?"]), "flag: none");
    check!("<Flag as Decoder>::NAME", <Flag as Decoder>::NAME, "flag");
}

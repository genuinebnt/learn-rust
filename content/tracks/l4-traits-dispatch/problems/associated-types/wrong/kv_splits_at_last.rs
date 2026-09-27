use std::fmt::Debug;

pub struct Celsius(pub f64);
pub struct Fahrenheit(pub f64);
pub struct Kelvin(pub f64);

/// Decodes "1, 2, 3" into integers.
pub struct CsvInts;
/// Decodes "key=value" into a pair.
pub struct KeyValue;

pub trait Convert<T> {
    fn convert(&self) -> T;
}

impl Convert<Fahrenheit> for Celsius {
    fn convert(&self) -> Fahrenheit {
        Fahrenheit(self.0 * 9.0 / 5.0 + 32.0)
    }
}

impl Convert<Kelvin> for Celsius {
    fn convert(&self) -> Kelvin {
        Kelvin(self.0 + 273.15)
    }
}

pub trait Decoder {
    type Output;
    const NAME: &'static str;

    fn decode(&self, input: &str) -> Option<Self::Output>;
}

impl Decoder for CsvInts {
    type Output = Vec<i64>;
    const NAME: &'static str = "csv";

    fn decode(&self, input: &str) -> Option<Vec<i64>> {
        if input.trim().is_empty() {
            return Some(Vec::new());
        }
        input.split(',').map(|p| p.trim().parse().ok()).collect()
    }
}

impl Decoder for KeyValue {
    type Output = (String, String);
    const NAME: &'static str = "kv";

    fn decode(&self, input: &str) -> Option<(String, String)> {
        let (k, v) = input.rsplit_once('=')?;
        Some((k.trim().to_string(), v.trim().to_string()))
    }
}

/// Decodes every item, skipping the ones that fail.
pub fn decode_all<D: Decoder>(d: &D, items: &[&str]) -> Vec<D::Output> {
    items.iter().filter_map(|s| d.decode(s)).collect()
}

/// "<NAME>: <first item that decodes, in Debug form>", or "<NAME>: none".
pub fn first_decoded<D>(d: &D, items: &[&str]) -> String
where
    D: Decoder,
    D::Output: Debug,
{
    match items.iter().find_map(|s| d.decode(s)) {
        Some(out) => format!("{}: {:?}", D::NAME, out),
        None => format!("{}: none", D::NAME),
    }
}

/// The temperature in the two other scales.
pub fn to_both(c: &Celsius) -> (Fahrenheit, Kelvin) {
    (c.convert(), <Celsius as Convert<Kelvin>>::convert(c))
}

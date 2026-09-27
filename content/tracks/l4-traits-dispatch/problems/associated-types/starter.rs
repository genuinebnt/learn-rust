use std::fmt::Debug;

pub struct Celsius(pub f64);
pub struct Fahrenheit(pub f64);
pub struct Kelvin(pub f64);

/// Decodes "1, 2, 3" into integers.
pub struct CsvInts;
/// Decodes "key=value" into a pair.
pub struct KeyValue;

// TODO: the Convert<T> and Decoder traits, and their impls.

/// Decodes every item, skipping the ones that fail.
pub fn decode_all<D: Decoder>(d: &D, items: &[&str]) -> Vec<D::Output> {
    items.iter().filter_map(|s| d.decode(s)).collect()
}

/// "<NAME>: <first item that decodes, in Debug form>", or "<NAME>: none".
pub fn first_decoded<D>(d: &D, items: &[&str]) -> String
// TODO: the where clause
{
    todo!()
}

/// The temperature in the two other scales.
pub fn to_both(c: &Celsius) -> (Fahrenheit, Kelvin) {
    todo!()
}

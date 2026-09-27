/// Parses a value from text that lives for `'de`. Types that borrow from the text (`&'de str`) and types
/// that own their data (`u32`, `String`, `Vec<u32>`) can both implement it.
pub trait Decode<'de>: Sized {
    fn decode(input: &'de str) -> Option<Self>;
}

impl<'de> Decode<'de> for &'de str {
    fn decode(input: &'de str) -> Option<Self> {
        (!input.is_empty()).then_some(input)
    }
}

impl<'de> Decode<'de> for u32 {
    fn decode(input: &'de str) -> Option<Self> {
        input.parse().ok()
    }
}

impl<'de> Decode<'de> for String {
    fn decode(input: &'de str) -> Option<Self> {
        Some(input.to_string())
    }
}

/// Comma-separated items; an empty input is an empty list, and any bad item fails the whole list.
impl<'de, T: Decode<'de>> Decode<'de> for Vec<T> {
    fn decode(input: &'de str) -> Option<Self> {
        if input.is_empty() {
            return Some(Vec::new());
        }
        input.split(',').map(T::decode).collect()
    }
}

/// Decodes each line exactly as written, borrowing from `text` where the type allows.
pub fn decode_lines<'de, T: Decode<'de>>(text: &'de str) -> Vec<Option<T>> {
    text.lines().map(T::decode).collect()
}

/// Decodes each line after trimming and lowercasing it. The cleaned lines are temporary, so only types that
/// own their data can come out.
pub fn decode_normalized<'de, T: Decode<'de>>(text: &str) -> Vec<Option<T>> {
    text.lines()
        .map(|line| {
            let clean = line.trim().to_lowercase();
            T::decode(&clean)
        })
        .collect()
}

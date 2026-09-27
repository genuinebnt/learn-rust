/// The chosen colour, else the palette's first colour, else "black".
pub fn theme<'a>(chosen: Option<&'a str>, palette: &[&'a str]) -> &'a str {
    if chosen.is_none() && palette.is_empty() {
        return "black";
    }
    chosen.unwrap_or_else(|| palette[0])
}

/// The byte length of the colour `theme` would pick, but 0 instead of "black".
pub fn theme_len(chosen: Option<&str>, palette: &[&str]) -> usize {
    if chosen.is_none() && palette.is_empty() {
        return 0;
    }
    chosen.map_or_else(|| palette[0].len(), str::len)
}

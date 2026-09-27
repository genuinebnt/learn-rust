/// The chosen colour, else the palette's first colour, else "black".
pub fn theme<'a>(chosen: Option<&'a str>, palette: &[&'a str]) -> &'a str {
    if chosen.is_none() && palette.is_empty() {
        return "black";
    }
    palette.first().copied().or(chosen).unwrap_or("black")
}

/// The byte length of the colour `theme` would pick, but 0 instead of "black".
pub fn theme_len(chosen: Option<&str>, palette: &[&str]) -> usize {
    if chosen.is_none() && palette.is_empty() {
        return 0;
    }
    palette.first().or(chosen.as_ref()).map_or(0, |s| s.len())
}

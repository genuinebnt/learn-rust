use std::borrow::Cow;
use std::ffi::OsStr;
use std::path::{Path, PathBuf};

/// The extension, ASCII-lowercased, if the file name has one that is valid UTF-8.
pub fn ext_lower(path: &Path) -> Option<String> {
    Some(path.extension()?.to_str()?.to_ascii_lowercase())
}

/// The file name for display, with U+FFFD for bytes that aren't UTF-8; "" when there is no file name.
pub fn display_name(path: &Path) -> Cow<'_, str> {
    path.file_name().map_or(Cow::Borrowed(""), OsStr::to_string_lossy)
}

/// The same path with ".bak" appended to the file name; `None` when there is no file name.
pub fn backup_path(path: &Path) -> Option<PathBuf> {
    let mut name = path.file_name()?.to_os_string();
    name.push(".bak");
    Some(path.with_file_name(name))
}

/// The paths that are inside `root` (by whole components), relative to it and as UTF-8, in order.
pub fn relative_to<'a>(paths: &'a [PathBuf], root: &Path) -> Vec<&'a str> {
    let root = root.to_str().unwrap_or("").trim_end_matches('/');
    paths.iter().filter_map(|p| Some(p.to_str()?.strip_prefix(root)?.trim_start_matches('/'))).collect()
}

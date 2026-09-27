use std::borrow::Cow;
use std::ffi::OsStr;
use std::path::{Path, PathBuf};

/// The extension, ASCII-lowercased, if the file name has one that is valid UTF-8.
pub fn ext_lower(path: &Path) -> Option<String> {
    todo!()
}

/// The file name for display, with U+FFFD for bytes that aren't UTF-8; "" when there is no file name.
pub fn display_name(path: &Path) -> Cow<'_, str> {
    todo!()
}

/// The same path with ".bak" appended to the file name; `None` when there is no file name.
pub fn backup_path(path: &Path) -> Option<PathBuf> {
    todo!()
}

/// The paths that are inside `root` (by whole components), relative to it and as UTF-8, in order.
pub fn relative_to<'a>(paths: &'a [PathBuf], root: &Path) -> Vec<&'a str> {
    todo!()
}

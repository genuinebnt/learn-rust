use solution::*;

use std::ffi::OsStr;
use std::os::unix::ffi::OsStrExt;
use std::path::{Path, PathBuf};

/// A path from raw bytes, which need not be UTF-8 (Unix paths are bytes).
fn raw(bytes: &[u8]) -> &Path {
    Path::new(OsStr::from_bytes(bytes))
}

fn bufs(paths: &[&str]) -> Vec<PathBuf> {
    paths.iter().map(PathBuf::from).collect()
}

#[test]
fn ext_lowercased() {
    check!(r#""photos/IMG_01.JPG""#, ext_lower(Path::new("photos/IMG_01.JPG")), Some("jpg".to_string()));
}

#[test]
fn dotfile_has_no_extension() {
    check!(r#"".bashrc""#, ext_lower(Path::new(".bashrc")), None);
}

#[test]
fn display_non_utf8_name() {
    check!(r#"b"dir/caf\xe9.txt" (Latin-1 é)"#, display_name(raw(b"dir/caf\xe9.txt")), "caf\u{FFFD}.txt");
}

#[test]
fn backup_appends() {
    check!(r#""conf/notes.txt""#, backup_path(Path::new("conf/notes.txt")), Some(PathBuf::from("conf/notes.txt.bak")));
}

#[test]
fn relative_by_components() {
    let paths = bufs(&["/data/a.txt", "/data2/b", "/data/x/y"]);
    check!(r#"root "/data", paths ["/data/a.txt", "/data2/b", "/data/x/y"]"#, relative_to(&paths, Path::new("/data")), vec!["a.txt", "x/y"]);
}

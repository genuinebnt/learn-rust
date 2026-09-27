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
fn ext_last_one_only() {
    check!(r#""a.tar.GZ""#, ext_lower(Path::new("a.tar.GZ")), Some("gz".to_string()));
}

#[test]
fn ext_trailing_dot_is_empty() {
    check!(r#""file.""#, ext_lower(Path::new("file.")), Some(String::new()));
}

#[test]
fn ext_dot_in_directory() {
    check!(r#""dir.d/file""#, ext_lower(Path::new("dir.d/file")), None);
}

#[test]
fn ext_hidden_file_with_extension() {
    check!(r#""x/.env.LOCAL""#, ext_lower(Path::new("x/.env.LOCAL")), Some("local".to_string()));
}

#[test]
fn ext_not_utf8() {
    check!(r#"b"a.t\xffxt""#, ext_lower(raw(b"a.t\xffxt")), None);
}

#[test]
fn ext_only_ascii_lowered() {
    check!(r#""a.ÉTÉ""#, ext_lower(Path::new("a.ÉTÉ")), Some("ÉtÉ".to_string()));
}

#[test]
fn ext_no_file_name() {
    check!(r#""/" and "..""#, (ext_lower(Path::new("/")), ext_lower(Path::new(".."))), (None, None));
}

#[test]
fn display_borrows_utf8() {
    check!(r#""a/b/日本.txt""#, matches!(display_name(Path::new("a/b/日本.txt")), std::borrow::Cow::Borrowed("日本.txt")), true);
}

#[test]
fn display_no_file_name() {
    check!(r#""/", "..", "a/..", """#, [display_name(Path::new("/")), display_name(Path::new("..")), display_name(Path::new("a/..")), display_name(Path::new(""))], ["", "", "", ""]);
}

#[test]
fn display_trailing_slash() {
    check!(r#""a/b/""#, display_name(Path::new("a/b/")), "b");
}

#[test]
fn backup_not_with_extension() {
    check!(r#""a/b.tar.gz""#, backup_path(Path::new("a/b.tar.gz")), Some(PathBuf::from("a/b.tar.gz.bak")));
}

#[test]
fn backup_no_extension() {
    check!(r#""Makefile""#, backup_path(Path::new("Makefile")), Some(PathBuf::from("Makefile.bak")));
}

#[test]
fn backup_dotfile() {
    check!(r#""~/.bashrc""#, backup_path(Path::new("~/.bashrc")), Some(PathBuf::from("~/.bashrc.bak")));
}

#[test]
fn backup_non_utf8() {
    check!(r#"b"d/\xff.log""#, backup_path(raw(b"d/\xff.log")), Some(raw(b"d/\xff.log.bak").to_path_buf()));
}

#[test]
fn backup_no_file_name() {
    check!(r#""/" and "x/..""#, (backup_path(Path::new("/")), backup_path(Path::new("x/.."))), (None, None));
}

#[test]
fn backup_trailing_slash() {
    check!(r#""logs/""#, backup_path(Path::new("logs/")), Some(PathBuf::from("logs.bak")));
}

#[test]
fn relative_root_itself_and_trailing_slash() {
    let paths = bufs(&["/data", "/data/", "/database"]);
    check!(r#"root "/data/", paths ["/data", "/data/", "/database"]"#, relative_to(&paths, Path::new("/data/")), vec!["", ""]);
}

#[test]
fn relative_skips_non_utf8() {
    let paths = vec![PathBuf::from("/r/ok"), raw(b"/r/\xff").to_path_buf(), PathBuf::from("/r/fine")];
    check!(r#"root "/r", paths ["/r/ok", b"/r/\xff", "/r/fine"]"#, relative_to(&paths, Path::new("/r")), vec!["ok", "fine"]);
}

#[test]
fn relative_relative_paths() {
    let paths = bufs(&["src/lib.rs", "srcs/x", "./src/a", "src"]);
    check!(r#"root "src", paths ["src/lib.rs", "srcs/x", "./src/a", "src"]"#, relative_to(&paths, Path::new("src")), vec!["lib.rs", ""]);
}

#[test]
fn relative_borrows() {
    let paths = bufs(&["/r/abc"]);
    let got = relative_to(&paths, Path::new("/r"));
    check!(r#"the result points into the input paths"#, got[0].as_ptr() == paths[0].to_str().unwrap()[3..].as_ptr(), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7215);
    let parts = ["a", "ab", "a.b", ".c", "d.", "X.Y"];
    for _ in 0..300 {
        let n = rng.below(4) + 1;
        let comps: Vec<&str> = (0..n).map(|_| *rng.pick(&parts)).collect();
        let path = comps.join("/");
        let name = *comps.last().unwrap();
        let want_ext = match name.rfind('.') {
            Some(0) | None => None,
            Some(i) => Some(name[i + 1..].to_ascii_lowercase()),
        };
        let want_bak = PathBuf::from(format!("{path}.bak"));
        let root_len = rng.below(n + 1);
        let root = comps[..root_len].join("/");
        let want_rel: Vec<String> = if root_len == 0 { vec![path.clone()] } else { vec![comps[root_len..].join("/")] };
        let paths = vec![PathBuf::from(&path)];
        let got_rel: Vec<String> = relative_to(&paths, Path::new(&root)).into_iter().map(String::from).collect();
        check!(format!("path = {path:?}, root = {root:?}"),
               (ext_lower(Path::new(&path)), display_name(Path::new(&path)).into_owned(), backup_path(Path::new(&path)), got_rel),
               (want_ext, name.to_string(), Some(want_bak), want_rel));
    }
}

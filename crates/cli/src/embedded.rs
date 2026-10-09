//! The courses compiled into the binary (see build.rs): `anneal course init bustub` works from any directory, with no checkout.
//! The files are written once to a cache directory named after the content, and the rest of the CLI reads them from there as it reads
//! a `courses/` directory.

use std::fs;
use std::path::{Path, PathBuf};

use anyhow::Context;

static BLOB: &[u8] = include_bytes!(concat!(env!("OUT_DIR"), "/courses.bin"));

/// The embedded files as (relative path, bytes).
fn entries(blob: &[u8]) -> Vec<(&str, &[u8])> {
    let mut out = Vec::new();
    let mut at = 0;
    while at + 4 <= blob.len() {
        let plen = u32::from_le_bytes(blob[at..at + 4].try_into().unwrap()) as usize;
        at += 4;
        let path = std::str::from_utf8(&blob[at..at + plen]).unwrap_or("");
        at += plen;
        let dlen = u64::from_le_bytes(blob[at..at + 8].try_into().unwrap()) as usize;
        at += 8;
        out.push((path, &blob[at..at + dlen]));
        at += dlen;
    }
    out
}

/// FNV-1a: names the cache directory after the content, so a new build never reads an old extraction.
fn fingerprint(blob: &[u8]) -> u64 {
    blob.iter().fold(0xcbf2_9ce4_8422_2325u64, |h, b| (h ^ u64::from(*b)).wrapping_mul(0x0000_0100_0000_01b3))
}

fn cache_base() -> Option<PathBuf> {
    std::env::var_os("XDG_CACHE_HOME").map(PathBuf::from).or_else(|| std::env::var_os("HOME").map(|h| PathBuf::from(h).join(".cache"))).map(|b| b.join("anneal"))
}

/// The `courses/` directory holding the embedded courses, written if it is not there yet. `None` if the binary carries no courses.
pub fn courses_dir() -> anyhow::Result<Option<PathBuf>> {
    if BLOB.is_empty() {
        return Ok(None);
    }
    let base = cache_base().context("no home directory for the course cache")?;
    let dir = base.join(format!("courses-{:016x}", fingerprint(BLOB)));
    if !dir.join(".complete").exists() {
        extract(BLOB, &dir)?;
    }
    Ok(Some(dir))
}

fn extract(blob: &[u8], dir: &Path) -> anyhow::Result<()> {
    for (rel, data) in entries(blob) {
        let target = dir.join(rel);
        fs::create_dir_all(target.parent().context("a file has no parent")?)?;
        fs::write(&target, data).with_context(|| format!("writing {}", target.display()))?;
    }
    fs::write(dir.join(".complete"), b"")?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_blob_round_trips_through_extraction() {
        let mut blob = Vec::new();
        for (path, data) in [("c/course.toml", &b"id = \"c\"\n"[..]), ("c/template/src/lib.rs", &b"// hi\n"[..])] {
            blob.extend((path.len() as u32).to_le_bytes());
            blob.extend(path.as_bytes());
            blob.extend((data.len() as u64).to_le_bytes());
            blob.extend(data);
        }
        assert_eq!(entries(&blob).len(), 2);
        let dir = std::env::temp_dir().join(format!("anneal-embedded-test-{}", std::process::id()));
        extract(&blob, &dir).unwrap();
        assert_eq!(fs::read_to_string(dir.join("c/template/src/lib.rs")).unwrap(), "// hi\n");
        assert!(dir.join(".complete").exists());
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn the_fingerprint_changes_with_the_content() {
        assert_ne!(fingerprint(b"a"), fingerprint(b"b"));
        assert_eq!(fingerprint(b"same"), fingerprint(b"same"));
    }
}

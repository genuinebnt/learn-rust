//! The crates problems may depend on: the `[dependencies]` of `docker/deps/Cargo.toml`, pinned by
//! its `Cargo.lock`. The sandbox image vendors exactly this set into [`VENDOR_DIR`].

const MANIFEST: &str = include_str!("../../../docker/deps/Cargo.toml");
const LOCK: &str = include_str!("../../../docker/deps/Cargo.lock");

/// Where the runner image keeps the vendored sources.
pub const VENDOR_DIR: &str = "/opt/anneal-vendor";

/// `(name, full dependency line)` for every allowed crate, in manifest order.
fn entries() -> impl Iterator<Item = (&'static str, &'static str)> {
    MANIFEST
        .lines()
        .skip_while(|l| l.trim() != "[dependencies]")
        .skip(1)
        .take_while(|l| !l.trim_start().starts_with('['))
        .map(str::trim)
        .filter(|l| !l.is_empty() && !l.starts_with('#'))
        .filter_map(|l| Some((l.split_once(" = ")?.0, l)))
}

/// Names of the crates a problem may use.
pub fn known_crates() -> Vec<&'static str> {
    entries().map(|(name, _)| name).collect()
}

/// The `[dependencies]` lines for `crates`, or the first unknown name.
pub(crate) fn dependency_lines(crates: &[String]) -> Result<String, String> {
    let mut out = String::new();
    for c in crates {
        let (_, line) = entries().find(|(name, _)| name == c).ok_or_else(|| c.clone())?;
        out.push_str(line);
        out.push('\n');
    }
    Ok(out)
}

/// The pinned lockfile, so every run resolves to the vendored versions.
pub(crate) fn lockfile() -> &'static str {
    LOCK
}

/// Cargo config that swaps crates.io for the vendored copy in the image.
pub(crate) fn vendor_config() -> String {
    format!(
        "[source.crates-io]\nreplace-with = \"anneal-vendor\"\n\n[source.anneal-vendor]\ndirectory = \"{VENDOR_DIR}\"\n"
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn lists_the_crate_set() {
        let known = known_crates();
        for name in ["tokio", "serde", "anyhow", "thiserror", "rand", "clap"] {
            assert!(known.contains(&name), "{name} missing from {known:?}");
        }
    }

    #[test]
    fn copies_lines_and_rejects_unknown_crates() {
        let lines = dependency_lines(&["serde".into(), "anyhow".into()]).unwrap();
        assert!(lines.starts_with("serde = { version = \"1\", features = [\"derive\"] }\n"), "{lines}");
        assert!(lines.contains("anyhow = \"1\""));
        assert_eq!(dependency_lines(&["left-pad".into()]), Err("left-pad".into()));
    }
}

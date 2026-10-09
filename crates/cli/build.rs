//! Packs the learner-facing part of every course (course.toml, lectures.toml, modules/, template/) into one blob that is compiled into the
//! binary, so `cargo install --git ...` gives an `anneal` that can `course init` with no checkout of the repository. The reference solution
//! is never included (it is not part of those directories). A missing `courses/` directory (a build context without it) gives an empty blob.
//!
//! Blob format: repeated `[u32 path length][path bytes][u64 data length][data bytes]`, little-endian, paths relative to `courses/`.

use std::fs;
use std::io::Write;
use std::path::{Path, PathBuf};

fn walk(base: &Path, dir: &Path, out: &mut Vec<PathBuf>) {
    let Ok(entries) = fs::read_dir(dir) else { return };
    let mut entries: Vec<_> = entries.flatten().map(|e| e.path()).collect();
    entries.sort();
    for p in entries {
        if p.is_dir() {
            walk(base, &p, out);
        } else if p.file_name().is_some_and(|n| n != ".DS_Store") {
            out.push(p.strip_prefix(base).unwrap().to_path_buf());
        }
    }
}

fn main() {
    let manifest = PathBuf::from(std::env::var("CARGO_MANIFEST_DIR").unwrap());
    let courses = manifest.join("../../courses");
    let mut files: Vec<PathBuf> = Vec::new();
    if let Ok(ids) = fs::read_dir(&courses) {
        let mut ids: Vec<_> = ids.flatten().map(|e| e.path()).filter(|p| p.join("course.toml").is_file()).collect();
        ids.sort();
        for id in ids {
            let name = id.file_name().unwrap().to_owned();
            for single in ["course.toml", "lectures.toml"] {
                if id.join(single).is_file() {
                    files.push(Path::new(&name).join(single));
                }
            }
            for sub in ["modules", "template"] {
                walk(&courses, &id.join(sub), &mut files);
                println!("cargo:rerun-if-changed={}", id.join(sub).display());
            }
            println!("cargo:rerun-if-changed={}", id.join("course.toml").display());
            println!("cargo:rerun-if-changed={}", id.join("lectures.toml").display());
        }
    }
    println!("cargo:rerun-if-changed={}", courses.display());
    let mut blob: Vec<u8> = Vec::new();
    for rel in &files {
        let data = fs::read(courses.join(rel)).unwrap();
        let path = rel.to_string_lossy().replace('\\', "/");
        blob.write_all(&(path.len() as u32).to_le_bytes()).unwrap();
        blob.write_all(path.as_bytes()).unwrap();
        blob.write_all(&(data.len() as u64).to_le_bytes()).unwrap();
        blob.write_all(&data).unwrap();
    }
    let out = PathBuf::from(std::env::var("OUT_DIR").unwrap()).join("courses.bin");
    fs::write(out, blob).unwrap();
}

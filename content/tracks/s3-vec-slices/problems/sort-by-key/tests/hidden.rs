use solution::*;

fn files(spec: &[(&str, u64)]) -> Vec<File> {
    spec.iter().map(|&(name, size)| File { name: name.to_string(), size }).collect()
}

fn names(fs: &[File]) -> Vec<&str> {
    fs.iter().map(|f| f.name.as_str()).collect()
}

fn players(spec: &[(&str, u32, u32)]) -> Vec<(String, u32, u32)> {
    spec.iter().map(|&(n, w, l)| (n.to_string(), w, l)).collect()
}

#[test]
fn no_extension_first() {
    let mut f = files(&[("x.a", 1), ("README", 1), ("LICENSE", 9)]);
    sort_files(&mut f);
    check!(r#"files = [("x.a", 1), ("README", 1), ("LICENSE", 9)]"#, names(&f), vec!["LICENSE", "README", "x.a"]);
}

#[test]
fn last_dot_counts() {
    let mut f = files(&[("a.tar.gz", 1), ("b.gz", 2), ("c.tar", 3)]);
    sort_files(&mut f);
    check!(r#"files = [("a.tar.gz", 1), ("b.gz", 2), ("c.tar", 3)]"#, names(&f), vec!["b.gz", "a.tar.gz", "c.tar"]);
}

#[test]
fn case_insensitive_extension() {
    let mut f = files(&[("a.Rs", 1), ("b.rS", 2), ("c.RS", 3)]);
    sort_files(&mut f);
    check!(r#"files = [("a.Rs", 1), ("b.rS", 2), ("c.RS", 3)]"#, names(&f), vec!["c.RS", "b.rS", "a.Rs"]);
}

#[test]
fn trailing_dot_is_empty_extension() {
    let mut f = files(&[("a.", 1), ("b", 1), ("c.a", 1)]);
    sort_files(&mut f);
    check!(r#"files = [("a.", 1), ("b", 1), ("c.a", 1)]"#, names(&f), vec!["b", "a.", "c.a"]);
}

#[test]
fn empty_files() {
    check!(r#"[]"#, { let mut f: Vec<File> = vec![]; sort_files(&mut f); f.len() }, 0);
}

#[test]
fn leaderboard_single() {
    let mut p = players(&[("solo", 0, 0)]);
    leaderboard(&mut p);
    check!(r#"players (name, wins, losses) = [("solo", 0, 0)]"#, p.iter().map(|p| p.0.as_str()).collect::<Vec<_>>(), vec!["solo"]);
}

#[test]
fn leaderboard_all_tied_but_name() {
    let mut p = players(&[("c", 1, 1), ("a", 1, 1), ("b", 1, 1)]);
    leaderboard(&mut p);
    check!(r#"players (name, wins, losses) = [("c", 1, 1), ("a", 1, 1), ("b", 1, 1)]"#, p.iter().map(|p| p.0.as_str()).collect::<Vec<_>>(), vec!["a", "b", "c"]);
}

#[test]
fn leaderboard_max_values() {
    let mut p = players(&[("x", 4294967295, 4294967295), ("y", 4294967295, 0), ("z", 0, 0)]);
    leaderboard(&mut p);
    check!(r#"players (name, wins, losses) = [("x", 4294967295, 4294967295), ("y", 4294967295, 0), ("z", 0, 0)]"#, p.iter().map(|p| p.0.as_str()).collect::<Vec<_>>(), vec!["y", "x", "z"]);
}

#[test]
fn readings_negative_nan_first() {
    let mut v = [0.0, -f64::NAN, f64::NAN, -1.0];
    sort_readings(&mut v);
    check!(r#"[0.0, -NaN, NaN, -1.0]"#, (v[0].is_nan() && v[0].is_sign_negative(), v[1], v[2], v[3].is_nan() && v[3].is_sign_positive()), (true, -1.0, 0.0, true));
}

#[test]
fn readings_infinities() {
    let mut v = [f64::INFINITY, f64::NEG_INFINITY, 0.0];
    sort_readings(&mut v);
    check!(r#"[inf, -inf, 0.0]"#, v, [f64::NEG_INFINITY, 0.0, f64::INFINITY]);
}

#[test]
fn readings_empty() {
    check!(r#"[]"#, { let mut v: [f64; 0] = []; sort_readings(&mut v); v.len() }, 0);
}

#[test]
fn readings_many_nans_do_not_panic() {
    let mut v: Vec<f64> = (0..1000).map(|i| if i % 3 == 2 { f64::NAN } else { (i * 7919 % 1000) as f64 - 500.0 }).collect();
    sort_readings(&mut v);
    check!(r#"1000 values, every third NaN"#, (v[..667].iter().all(|x| !x.is_nan()), v[667..].iter().all(|x| x.is_nan()), v[..667].windows(2).all(|w| w[0] <= w[1])), (true, true, true));
}

#[test]
fn random_stability_vs_stable_sort() {
    let mut rng = anneal_prelude::Rng::new(7303);
    let exts = ["", ".a", ".A", ".b", ".B"];
    for round in 0..200 {
        let n = rng.below(60);
        let fs: Vec<File> = (0..n).map(|i| File { name: format!("f{i}{}", rng.pick(&exts)), size: rng.below(3) as u64 }).collect();
        let mut want = fs.clone();
        want.sort_by(|a, b| {
            let ka = a.name.rsplit_once('.').map(|(_, e)| e.to_ascii_lowercase());
            let kb = b.name.rsplit_once('.').map(|(_, e)| e.to_ascii_lowercase());
            ka.cmp(&kb).then(b.size.cmp(&a.size))
        });
        let mut got = fs.clone();
        sort_files(&mut got);
        check!(format!("round {round}: files = {:?}", names(&fs)), names(&got), names(&want));
    }
}

#[test]
fn cached_key_allocations() {
    let mut fs: Vec<File> = (0..2000u64).map(|i| File { name: format!("f{i}.EXT{}", i % 7), size: i * 7919 % 1000 }).collect();
    let ((), n) = anneal_prelude::allocs(|| sort_files(&mut fs));
    check!("2000 files: allocations while sorting (at most 3 per file)", n.count <= 6000, true);
}

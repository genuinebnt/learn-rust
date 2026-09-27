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
fn files_by_extension_then_size() {
    let mut f = files(&[("b.TXT", 1), ("a.rs", 5), ("c.txt", 9), ("Makefile", 2)]);
    sort_files(&mut f);
    check!(r#"files = [("b.TXT", 1), ("a.rs", 5), ("c.txt", 9), ("Makefile", 2)]"#, names(&f), vec!["Makefile", "a.rs", "c.txt", "b.TXT"]);
}

#[test]
fn ties_keep_input_order() {
    let mut f = files(&[("z.md", 3), ("a.md", 3), ("m.MD", 3)]);
    sort_files(&mut f);
    check!(r#"files = [("z.md", 3), ("a.md", 3), ("m.MD", 3)]"#, names(&f), vec!["z.md", "a.md", "m.MD"]);
}

#[test]
fn wins_then_losses_then_name() {
    let mut p = players(&[("cy", 3, 2), ("al", 5, 0), ("bo", 3, 1), ("di", 3, 1)]);
    leaderboard(&mut p);
    check!(r#"players (name, wins, losses) = [("cy", 3, 2), ("al", 5, 0), ("bo", 3, 1), ("di", 3, 1)]"#, p.iter().map(|p| p.0.as_str()).collect::<Vec<_>>(), vec!["al", "bo", "di", "cy"]);
}

#[test]
fn readings_with_nan_and_zeros() {
    let mut v = [1.0, f64::NAN, -0.0, 0.0, f64::NEG_INFINITY];
    sort_readings(&mut v);
    check!(r#"[1.0, NaN, -0.0, 0.0, -inf]"#, v.iter().map(|x| x.to_bits()).collect::<Vec<_>>() == [f64::NEG_INFINITY, -0.0, 0.0, 1.0, f64::NAN].iter().map(|x| x.to_bits()).collect::<Vec<_>>(), true);
}

#[test]
fn readings_plain() {
    let mut v = [3.5, -1.0, 2.0];
    sort_readings(&mut v);
    check!(r#"[3.5, -1.0, 2.0]"#, v, [-1.0, 2.0, 3.5]);
}

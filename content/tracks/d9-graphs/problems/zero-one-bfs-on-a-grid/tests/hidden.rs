use solution::*;

#[test]
fn walled_target() {
    check!(r#"grid = [".#"]"#, min_walls(&[".#"]), 1);
}

#[test]
fn detour_is_free() {
    check!(r###"grid = ["..#", "##.", "..."]"###, min_walls(&["..#", "##.", "..."]), 1);
}

#[test]
fn solid_rock() {
    let first = format!(".{}", "#".repeat(499));
    let rest = "#".repeat(500);
    let grid: Vec<&str> = (0..500).map(|i| if i == 0 { first.as_str() } else { rest.as_str() }).collect();
    check!(r#"500×500, all walls except the start"#, min_walls(&grid), 998);
}

#[test]
fn maze() {
    let rows: Vec<String> = (0..499).map(|r| if r % 2 == 0 { ".".repeat(500) } else if r % 4 == 1 { format!("{}.", "#".repeat(499)) } else { format!(".{}", "#".repeat(499)) }).collect();
    let grid: Vec<&str> = rows.iter().map(|s| s.as_str()).collect();
    check!(r#"499×500 snake of free corridors"#, min_walls(&grid), 0);
}

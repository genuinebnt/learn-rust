use solution::*;

#[test]
fn all_water() {
    check!(r#"grid = ["000"]"#, num_islands(&["000"]), 0);
}

#[test]
fn diagonal_not_connected() {
    check!(r#"grid = ["10", "01"]"#, num_islands(&["10", "01"]), 2);
}

#[test]
fn big_spiral() {
    let row = "1".repeat(300);
    let grid: Vec<&str> = (0..300).map(|_| row.as_str()).collect();
    check!(r#"300×300 all land"#, num_islands(&grid), 1);
}

#[test]
fn single_row() {
    check!(r#"grid = ["10101"]"#, num_islands(&["10101"]), 3);
}

#[test]
fn single_column() {
    check!(r#"grid = ["1", "0", "1", "1"]"#, num_islands(&["1", "0", "1", "1"]), 2);
}

#[test]
fn u_shape_joins_below() {
    check!(r#"grid = ["101", "101", "111"]"#, num_islands(&["101", "101", "111"]), 1);
}

#[test]
fn comb_joined_at_the_last_cell() {
    check!(r#"grid = ["10101", "10101", "10101", "11111"]"#, num_islands(&["10101", "10101", "10101", "11111"]), 1);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(905);
    for _ in 0..300 {
        let h = 1 + rng.below(6);
        let w = 1 + rng.below(6);
        let rows: Vec<String> = (0..h).map(|_| rng.string(w, "0011")).collect();
        let grid: Vec<&str> = rows.iter().map(|s| s.as_str()).collect();
        // Brute force: every land cell starts with its own label; spread the smallest label until nothing changes.
        let land: Vec<Vec<bool>> = rows.iter().map(|r| r.bytes().map(|b| b == b'1').collect()).collect();
        let mut label: Vec<Vec<usize>> = (0..h).map(|r| (0..w).map(|c| r * w + c).collect()).collect();
        loop {
            let mut changed = false;
            for r in 0..h {
                for c in 0..w {
                    if !land[r][c] {
                        continue;
                    }
                    for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                        if nr < h && nc < w && land[nr][nc] && label[nr][nc] < label[r][c] {
                            label[r][c] = label[nr][nc];
                            changed = true;
                        }
                    }
                }
            }
            if !changed {
                break;
            }
        }
        let want = (0..h).flat_map(|r| (0..w).map(move |c| (r, c))).filter(|&(r, c)| land[r][c] && label[r][c] == r * w + c).count();
        check!(format!("grid = {rows:?}"), num_islands(&grid), want);
    }
}

#[test]
fn scale_checkerboard_300() {
    let even: String = (0..300).map(|c| if c % 2 == 0 { '1' } else { '0' }).collect();
    let odd: String = (0..300).map(|c| if c % 2 == 1 { '1' } else { '0' }).collect();
    let grid: Vec<&str> = (0..300).map(|r| if r % 2 == 0 { even.as_str() } else { odd.as_str() }).collect();
    check!("300×300 checkerboard", num_islands(&grid), 45_000);
}

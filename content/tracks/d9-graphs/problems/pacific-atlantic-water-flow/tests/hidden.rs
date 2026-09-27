use solution::*;

#[test]
fn flat() {
    check!(r#"heights = [[3,3],[3,3]]"#, pacific_atlantic(&[vec![3, 3], vec![3, 3]]), vec![(0, 0), (0, 1), (1, 0), (1, 1)]);
}

#[test]
fn valley() {
    check!(r#"heights = [[5,1,5]]"#, pacific_atlantic(&[vec![5, 1, 5]]), vec![(0, 0), (0, 1), (0, 2)]);
}

#[test]
fn pit() {
    check!(r#"heights = [[3,3,3],[3,1,3],[3,3,3]]"#, pacific_atlantic(&[vec![3, 3, 3], vec![3, 1, 3], vec![3, 3, 3]]).len(), 8);
}

#[test]
fn single_column() {
    check!(r#"heights = [[3],[2],[1]]"#, pacific_atlantic(&[vec![3], vec![2], vec![1]]), vec![(0, 0), (1, 0), (2, 0)]);
}

#[test]
fn corner_only_pacific() {
    check!(r#"heights = [[1,2],[4,3]]"#, pacific_atlantic(&[vec![1, 2], vec![4, 3]]), vec![(0, 1), (1, 0), (1, 1)]);
}

#[test]
fn slope_to_the_atlantic() {
    check!(r#"heights = [[5,4,3],[4,3,2],[3,2,1]]"#, pacific_atlantic(&[vec![5, 4, 3], vec![4, 3, 2], vec![3, 2, 1]]), vec![(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)]);
}

#[test]
fn extreme_heights() {
    check!(r#"heights = [[MAX,0,MAX],[0,MAX,0],[MAX,0,MAX]] (MAX = u32::MAX)"#, pacific_atlantic(&[vec![u32::MAX, 0, u32::MAX], vec![0, u32::MAX, 0], vec![u32::MAX, 0, u32::MAX]]), vec![(0, 2), (1, 1), (2, 0)]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(909);
    for _ in 0..300 {
        let h = 1 + rng.below(5);
        let w = 1 + rng.below(5);
        let heights: Vec<Vec<u32>> = (0..h).map(|_| rng.vec(w, 0, 4)).collect();
        // Brute force: search downhill from every cell.
        let mut want = Vec::new();
        for r in 0..h {
            for c in 0..w {
                let mut seen = vec![vec![false; w]; h];
                seen[r][c] = true;
                let mut stack = vec![(r, c)];
                let (mut pacific, mut atlantic) = (false, false);
                while let Some((a, b)) = stack.pop() {
                    pacific |= a == 0 || b == 0;
                    atlantic |= a == h - 1 || b == w - 1;
                    for (x, y) in [(a.wrapping_sub(1), b), (a + 1, b), (a, b.wrapping_sub(1)), (a, b + 1)] {
                        if x < h && y < w && !seen[x][y] && heights[x][y] <= heights[a][b] {
                            seen[x][y] = true;
                            stack.push((x, y));
                        }
                    }
                }
                if pacific && atlantic {
                    want.push((r, c));
                }
            }
        }
        check!(format!("heights = {heights:?}"), pacific_atlantic(&heights), want);
    }
}

#[test]
fn scale_basin_300() {
    // A ring of height 10 around a flat basin of height 1: only the ring drains anywhere.
    let heights: Vec<Vec<u32>> = (0..300).map(|r| (0..300).map(|c| if r == 0 || c == 0 || r == 299 || c == 299 { 10 } else { 1 }).collect()).collect();
    let out = pacific_atlantic(&heights);
    check!("300×300 basin with a rim of height 10", (out.len(), out[0], out[298], out[299], out[1195]), (1196, (0, 0), (0, 298), (0, 299), (299, 299)));
}

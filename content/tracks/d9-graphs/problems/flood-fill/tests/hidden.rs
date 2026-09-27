use solution::*;

#[test]
fn same_colour_nonzero() {
    check!(r#"image = [[4,4],[4,4]], sr = 1, sc = 1, color = 4"#, flood_fill(vec![vec![4, 4], vec![4, 4]], 1, 1, 4), vec![vec![4, 4], vec![4, 4]]);
}

#[test]
fn start_in_a_corner() {
    check!(r#"image = [[0,0,1],[1,0,1],[1,1,0]], sr = 2, sc = 2, color = 7"#, flood_fill(vec![vec![0, 0, 1], vec![1, 0, 1], vec![1, 1, 0]], 2, 2, 7), vec![vec![0, 0, 1], vec![1, 0, 1], vec![1, 1, 7]]);
}

#[test]
fn whole_image() {
    check!(r#"image = 3×4 of 6, sr = 1, sc = 2, color = 1"#, flood_fill(vec![vec![6; 4]; 3], 1, 2, 1), vec![vec![1; 4]; 3]);
}

#[test]
fn largest_colour() {
    check!(r#"image = [[0,0],[1,0]], sr = 0, sc = 1, color = u32::MAX"#, flood_fill(vec![vec![0, 0], vec![1, 0]], 0, 1, u32::MAX), vec![vec![u32::MAX, u32::MAX], vec![1, u32::MAX]]);
}

#[test]
fn single_row() {
    check!(r#"image = [[1,1,0,1,1]], sr = 0, sc = 4, color = 2"#, flood_fill(vec![vec![1, 1, 0, 1, 1]], 0, 4, 2), vec![vec![1, 1, 0, 2, 2]]);
}

#[test]
fn around_a_wall() {
    check!(r#"image = [[1,1,1],[0,0,1],[1,1,1]], sr = 2, sc = 0, color = 5"#, flood_fill(vec![vec![1, 1, 1], vec![0, 0, 1], vec![1, 1, 1]], 2, 0, 5), vec![vec![5, 5, 5], vec![0, 0, 5], vec![5, 5, 5]]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(936);
    for _ in 0..300 {
        let (h, w) = (1 + rng.below(5), 1 + rng.below(5));
        let image: Vec<Vec<u32>> = (0..h).map(|_| rng.vec(w, 0, 2)).collect();
        let (sr, sc, color) = (rng.below(h), rng.below(w), rng.int(0, 3) as u32);
        // Brute force: grow the region until it stops changing, then paint it.
        let old = image[sr][sc];
        let mut region = vec![vec![false; w]; h];
        region[sr][sc] = true;
        let mut changed = true;
        while changed {
            changed = false;
            for r in 0..h {
                for c in 0..w {
                    let near = [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)];
                    if !region[r][c] && image[r][c] == old && near.iter().any(|&(a, b)| a < h && b < w && region[a][b]) {
                        region[r][c] = true;
                        changed = true;
                    }
                }
            }
        }
        let want: Vec<Vec<u32>> = (0..h).map(|r| (0..w).map(|c| if region[r][c] { color } else { image[r][c] }).collect()).collect();
        check!(format!("image = {image:?}, sr = {sr}, sc = {sc}, color = {color}"), flood_fill(image.clone(), sr, sc, color), want);
    }
}

#[test]
fn scale_snake_499x500() {
    // One corridor 125249 pixels long, winding through the whole image.
    let image: Vec<Vec<u32>> = (0..499).map(|r| if r % 2 == 0 { vec![1; 500] } else { let mut row = vec![0; 500]; row[if r % 4 == 1 { 499 } else { 0 }] = 1; row }).collect();
    let out = flood_fill(image, 0, 0, 7);
    let painted = out.iter().flatten().filter(|&&p| p == 7).count();
    check!("499×500 snake corridor, fill from (0, 0)", (painted, out[498][0], out[498][499], out[1][0]), (125_249, 7, 7, 0));
}

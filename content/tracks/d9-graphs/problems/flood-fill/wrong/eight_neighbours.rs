pub fn flood_fill(mut image: Vec<Vec<u32>>, sr: usize, sc: usize, color: u32) -> Vec<Vec<u32>> {
    let old = image[sr][sc];
    if old == color {
        return image;
    }
    let (h, w) = (image.len(), image[0].len());
    image[sr][sc] = color;
    let mut stack = vec![(sr, sc)];
    while let Some((r, c)) = stack.pop() {
        for dr in [usize::MAX, 0, 1] {
            for dc in [usize::MAX, 0, 1] {
                let (nr, nc) = (r.wrapping_add(dr), c.wrapping_add(dc));
                if nr < h && nc < w && image[nr][nc] == old {
                    image[nr][nc] = color;
                    stack.push((nr, nc));
                }
            }
        }
    }
    image
}

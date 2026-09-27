pub fn flood_fill(mut image: Vec<Vec<u32>>, sr: usize, sc: usize, color: u32) -> Vec<Vec<u32>> {
    let old = image[sr][sc];
    if old == color {
        return image;
    }
    let (h, w) = (image.len(), image[0].len());
    image[sr][sc] = color;
    let mut stack = vec![(sr, sc)];
    while let Some((r, c)) = stack.pop() {
        for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
            if nr < h && nc < w && image[nr][nc] == old {
                image[nr][nc] = color;
                stack.push((nr, nc));
            }
        }
    }
    image
}

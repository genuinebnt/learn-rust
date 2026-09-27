pub fn flood_fill(mut image: Vec<Vec<u32>>, sr: usize, sc: usize, color: u32) -> Vec<Vec<u32>> {
    fn paint(image: &mut Vec<Vec<u32>>, r: usize, c: usize, old: u32, color: u32) {
        if r >= image.len() || c >= image[0].len() || image[r][c] != old {
            return;
        }
        image[r][c] = color;
        paint(image, r.wrapping_sub(1), c, old, color);
        paint(image, r + 1, c, old, color);
        paint(image, r, c.wrapping_sub(1), old, color);
        paint(image, r, c + 1, old, color);
    }
    let old = image[sr][sc];
    if old != color {
        paint(&mut image, sr, sc, old, color);
    }
    image
}

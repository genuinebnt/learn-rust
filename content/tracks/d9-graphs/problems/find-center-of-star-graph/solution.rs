pub fn find_center(edges: &[(u32, u32)]) -> u32 {
    // The center is in every edge, so it's whichever end the first two edges share.
    let ((a, b), (c, d)) = (edges[0], edges[1]);
    if a == c || a == d {
        a
    } else {
        b
    }
}

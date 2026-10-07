pub fn find_center(edges: &[(u32, u32)]) -> u32 {
    let ((a, b), (c, _)) = (edges[0], edges[1]);
    if a == c {
        a
    } else {
        b
    }
}

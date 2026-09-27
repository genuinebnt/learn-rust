pub fn find_content_children(greed: &[u32], cookies: &[u32]) -> usize {
    let mut greed = greed.to_vec();
    let mut cookies = cookies.to_vec();
    greed.sort_unstable();
    cookies.sort_unstable();
    let mut happy = 0;
    for &size in &cookies {
        if happy < greed.len() && size >= greed[happy] {
            happy += 1;
        }
    }
    happy
}

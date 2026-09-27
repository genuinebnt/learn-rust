pub fn read_binary_watch(turned_on: u32) -> Vec<String> {
    let mut out = Vec::new();
    for h in 0..12u32 {
        for m in 0..60u32 {
            if h.count_ones() + m.count_ones() == turned_on {
                out.push(format!("{h}:{m}"));
            }
        }
    }
    out
}

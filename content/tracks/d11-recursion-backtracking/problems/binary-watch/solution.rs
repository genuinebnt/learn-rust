pub fn read_binary_watch(turned_on: u32) -> Vec<String> {
    // LEDs 0..4 are the hour bits 8, 4, 2, 1; LEDs 4..10 are the minute bits 32 … 1.
    fn go(led: u32, left: u32, hour: u32, minute: u32, out: &mut Vec<String>) {
        if hour > 11 || minute > 59 {
            return;
        }
        if left == 0 {
            out.push(format!("{hour}:{minute:02}"));
            return;
        }
        if led == 10 {
            return;
        }
        let (h, m) = if led < 4 { (8 >> led, 0) } else { (0, 32 >> (led - 4)) };
        go(led + 1, left - 1, hour + h, minute + m, out); // this LED on
        go(led + 1, left, hour, minute, out); // this LED off
    }
    let mut out = Vec::new();
    go(0, turned_on, 0, 0, &mut out);
    out
}

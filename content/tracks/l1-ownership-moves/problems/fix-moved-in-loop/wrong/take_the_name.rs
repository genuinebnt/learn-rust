/// Pushes "hello, <name>" into `out` three times.
pub fn greet_thrice(mut name: String, out: &mut Vec<String>) {
    for _ in 0..3 {
        out.push(greeting(std::mem::take(&mut name)));
    }
}

fn greeting(name: String) -> String {
    format!("hello, {name}")
}

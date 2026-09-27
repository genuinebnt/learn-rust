/// Pushes "hello, <name>" into `out` three times.
pub fn greet_thrice(name: String, out: &mut Vec<String>) {
    for _ in 0..3 {
        out.push(greeting(&name));
    }
}

fn greeting(name: &str) -> String {
    format!("hello, {name}")
}

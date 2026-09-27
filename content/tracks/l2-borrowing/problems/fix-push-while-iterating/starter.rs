/// For each task ending in '*', appends "<task>.1" and "<task>.2".
pub fn expand(tasks: &mut Vec<String>) {
    for t in tasks.iter() {
        if t.ends_with('*') {
            tasks.push(format!("{t}.1"));
            tasks.push(format!("{t}.2"));
        }
    }
}

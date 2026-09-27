/// For each task ending in '*', appends "<task>.1" and "<task>.2".
pub fn expand(tasks: &mut Vec<String>) {
    let mut out = Vec::new();
    for t in tasks.iter() {
        out.push(format!("{t}"));
        if t.ends_with('*') {
            out.push(format!("{t}.1"));
            out.push(format!("{t}.2"));
        }
    }
    *tasks = out;
}

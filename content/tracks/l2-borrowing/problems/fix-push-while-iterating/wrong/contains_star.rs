/// For each task ending in '*', appends "<task>.1" and "<task>.2".
pub fn expand(tasks: &mut Vec<String>) {
    let extra: Vec<String> = tasks
        .iter()
        .filter(|t| t.contains('*'))
        .flat_map(|t| [format!("{t}.1"), format!("{t}.2")])
        .collect();
    tasks.extend(extra);
}

use std::collections::HashMap;

/// Expands `tasks` in place: for every task in the list, including ones added by this call, each of its
/// subtasks in `rules` that isn't in the list yet is appended. Returns how many tasks were added.
pub fn expand(tasks: &mut Vec<String>, rules: &HashMap<String, Vec<String>>) -> usize {
    let before = tasks.len();
    let mut i = 0;
    while i < tasks.len() {
        if let Some(subs) = rules.get(&tasks[i]) {
            for s in subs {
                if !tasks.contains(s) {
                    tasks.push(s.to_string());
                }
            }
        }
        i += 1;
    }
    tasks.len() - before
}

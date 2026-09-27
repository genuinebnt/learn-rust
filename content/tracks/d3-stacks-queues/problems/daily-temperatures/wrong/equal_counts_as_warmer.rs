pub fn daily_temperatures(temps: &[i32]) -> Vec<usize> {
    let mut answer = vec![0; temps.len()];
    let mut waiting: Vec<usize> = Vec::new();
    for (i, &t) in temps.iter().enumerate() {
        while let Some(&j) = waiting.last() {
            if temps[j] > t {
                break;
            }
            answer[j] = i - j;
            waiting.pop();
        }
        waiting.push(i);
    }
    answer
}

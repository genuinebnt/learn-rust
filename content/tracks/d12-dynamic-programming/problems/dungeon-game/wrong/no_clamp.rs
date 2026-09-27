pub fn calculate_minimum_hp(dungeon: &[Vec<i32>]) -> i64 {
    let n = dungeon[0].len();
    let mut need = vec![i64::MAX; n + 1];
    need[n - 1] = 1;
    for row in dungeon.iter().rev() {
        for j in (0..n).rev() {
            let next = need[j].min(need[j + 1]);
            need[j] = next - row[j] as i64;
        }
    }
    need[0].max(1)
}

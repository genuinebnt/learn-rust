pub fn calculate_minimum_hp(dungeon: &[Vec<i32>]) -> i64 {
    let n = dungeon[0].len();
    // need[j] = the least health to enter room (i, j) and survive to the end.
    // Extra slot n and the "row below" start at MAX, except the princess's exit.
    let mut need = vec![i64::MAX; n + 1];
    need[n - 1] = 1;
    for row in dungeon.iter().rev() {
        for j in (0..n).rev() {
            let next = need[j].min(need[j + 1]); // down or right
            need[j] = (next - row[j] as i64).max(1);
        }
    }
    need[0]
}

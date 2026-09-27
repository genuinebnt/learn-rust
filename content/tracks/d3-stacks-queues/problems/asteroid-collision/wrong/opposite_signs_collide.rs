pub fn asteroid_collision(asteroids: &[i32]) -> Vec<i32> {
    let mut alive: Vec<i32> = Vec::new();
    'next: for &a in asteroids {
        while let Some(&top) = alive.last() {
            if (top > 0) == (a > 0) {
                break;
            }
            if top.abs() < a.abs() {
                alive.pop();
                continue;
            }
            if top.abs() == a.abs() {
                alive.pop();
            }
            continue 'next;
        }
        alive.push(a);
    }
    alive
}

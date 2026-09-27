pub fn asteroid_collision(asteroids: &[i32]) -> Vec<i32> {
    let mut alive: Vec<i32> = Vec::new();
    'next: for &a in asteroids {
        if a < 0 {
            while let Some(&top) = alive.last() {
                if top < 0 {
                    break;
                }
                if top < -a {
                    alive.pop();
                    continue;
                }
                if top == -a {
                    alive.pop();
                }
                continue 'next;
            }
        }
        alive.push(a);
    }
    alive
}

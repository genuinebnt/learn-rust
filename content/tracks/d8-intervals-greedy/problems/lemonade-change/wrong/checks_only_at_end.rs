pub fn lemonade_change(bills: &[u32]) -> bool {
    let (mut fives, mut tens) = (0i32, 0i32);
    for &bill in bills {
        match bill {
            5 => fives += 1,
            10 => {
                fives -= 1;
                tens += 1;
            }
            _ => {
                if tens > 0 {
                    tens -= 1;
                    fives -= 1;
                } else {
                    fives -= 3;
                }
            }
        }
    }
    fives >= 0 && tens >= 0
}

pub fn lemonade_change(bills: &[u32]) -> bool {
    let (mut fives, mut tens) = (0u32, 0u32);
    for &bill in bills {
        match bill {
            5 => fives += 1,
            10 => {
                if fives == 0 {
                    return false;
                }
                fives -= 1;
                tens += 1;
            }
            _ => {
                if tens > 0 && fives > 0 {
                    tens -= 1;
                    fives -= 1;
                } else if fives >= 3 {
                    fives -= 3;
                } else {
                    return false;
                }
            }
        }
    }
    true
}

fn wins(used: &mut Vec<bool>, left: u32) -> bool {
    for i in 0..used.len() {
        if !used[i] {
            let pick = i as u32 + 1;
            if pick >= left {
                return true;
            }
            used[i] = true;
            let other = wins(used, left - pick);
            used[i] = false;
            if !other {
                return true;
            }
        }
    }
    false
}

pub fn can_i_win(max_choosable: u32, desired_total: u32) -> bool {
    if desired_total == 0 {
        return true;
    }
    if max_choosable * (max_choosable + 1) / 2 < desired_total {
        return false;
    }
    wins(&mut vec![false; max_choosable as usize], desired_total)
}

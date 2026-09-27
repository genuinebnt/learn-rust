pub fn is_n_straight_hand(hand: &[i32], group_size: usize) -> bool {
    let mut cards = hand.to_vec();
    cards.sort_unstable();
    while let Some(&first) = cards.first() {
        for k in 0..group_size as i64 {
            match cards.iter().position(|&c| c as i64 == first as i64 + k) {
                Some(i) => {
                    cards.remove(i);
                }
                None => return false,
            }
        }
    }
    true
}

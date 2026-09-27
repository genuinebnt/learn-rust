use std::collections::BTreeSet;

pub fn is_n_straight_hand(hand: &[i32], group_size: usize) -> bool {
    if hand.len() % group_size != 0 {
        return false;
    }
    let cards: BTreeSet<i64> = hand.iter().map(|&c| c as i64).collect();
    cards.iter().all(|&c| cards.contains(&(c + 1)) || cards.contains(&(c - 1)) || group_size == 1)
}

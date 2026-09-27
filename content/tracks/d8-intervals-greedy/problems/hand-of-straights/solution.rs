use std::collections::BTreeMap;

pub fn is_n_straight_hand(hand: &[i32], group_size: usize) -> bool {
    if hand.len() % group_size != 0 {
        return false;
    }
    let mut counts: BTreeMap<i64, usize> = BTreeMap::new();
    for &card in hand {
        *counts.entry(card as i64).or_insert(0) += 1;
    }
    // The smallest card left must start a run; all `n` copies of it start `n` runs.
    while let Some((&first, &n)) = counts.first_key_value() {
        for card in first..first + group_size as i64 {
            match counts.get_mut(&card) {
                Some(c) if *c >= n => {
                    *c -= n;
                    if *c == 0 {
                        counts.remove(&card);
                    }
                }
                _ => return false,
            }
        }
    }
    true
}

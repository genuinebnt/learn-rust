use std::collections::BTreeMap;

pub fn is_n_straight_hand(hand: &[i32], group_size: usize) -> bool {
    if hand.len() % group_size != 0 {
        return false;
    }
    let mut counts: BTreeMap<i32, usize> = BTreeMap::new();
    for &card in hand {
        *counts.entry(card).or_insert(0) += 1;
    }
    while let Some((&first, &n)) = counts.first_key_value() {
        for card in first..first + group_size as i32 {
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

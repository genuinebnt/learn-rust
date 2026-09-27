use std::collections::VecDeque;

pub fn ladder_length(begin: &str, end: &str, words: &[&str]) -> usize {
    if !words.contains(&end) {
        return 0;
    }
    let differ_by_one = |a: &str, b: &str| a.bytes().zip(b.bytes()).filter(|(x, y)| x != y).count() == 1;
    let mut unseen: Vec<&str> = words.iter().copied().filter(|&w| w != begin).collect();
    let mut queue = VecDeque::from([(begin, 1)]);
    while let Some((w, steps)) = queue.pop_front() {
        if w == end {
            return steps;
        }
        let (next, rest): (Vec<&str>, Vec<&str>) = unseen.into_iter().partition(|&x| differ_by_one(w, x));
        unseen = rest;
        for x in next {
            queue.push_back((x, steps + 1));
        }
    }
    0
}

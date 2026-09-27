pub fn by_len_then_alpha(words: &mut [String]) {
    for i in 1..words.len() {
        let mut j = i;
        while j > 0 && (words[j].len(), &words[j]) < (words[j - 1].len(), &words[j - 1]) {
            words.swap(j, j - 1);
            j -= 1;
        }
    }
}

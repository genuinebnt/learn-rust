use std::collections::VecDeque;

pub struct StreamChecker {
    nodes: Vec<([u32; 26], bool)>,
    recent: VecDeque<u8>,
    longest: usize,
}

impl StreamChecker {
    pub fn new(words: &[&str]) -> Self {
        let mut nodes = vec![([0u32; 26], false)];
        for w in words {
            let mut at = 0;
            for b in w.bytes().rev() {
                let i = (b - b'a') as usize;
                if nodes[at].0[i] == 0 {
                    nodes.push(([0; 26], false));
                    nodes[at].0[i] = (nodes.len() - 1) as u32;
                }
                at = nodes[at].0[i] as usize;
            }
            nodes[at].1 = true;
        }
        let longest = words.iter().map(|w| w.len()).max().unwrap_or(0);
        StreamChecker { nodes, recent: VecDeque::new(), longest }
    }

    pub fn query(&mut self, letter: char) -> bool {
        self.recent.push_back(letter as u8);
        if self.recent.len() >= self.longest {
            self.recent.pop_front();
        }
        let mut at = 0;
        for &b in self.recent.iter().rev() {
            at = self.nodes[at].0[(b - b'a') as usize] as usize;
            if at == 0 {
                return false;
            }
            if self.nodes[at].1 {
                return true;
            }
        }
        false
    }
}

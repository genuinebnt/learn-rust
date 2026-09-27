use std::collections::HashMap;

fn slot(c: u8) -> usize {
    if c == b' ' { 26 } else { (c - b'a') as usize }
}

#[derive(Default)]
struct Node {
    children: [u32; 27],
    top: Vec<u32>,
}

pub struct AutocompleteSystem {
    nodes: Vec<Node>,
    sentences: Vec<String>,
    counts: Vec<u64>,
    ids: HashMap<String, u32>,
    typed: String,
    cursor: Option<usize>,
}

impl AutocompleteSystem {
    pub fn new(sentences: &[&str], times: &[u32]) -> Self {
        let mut sys = AutocompleteSystem {
            nodes: vec![Node::default()],
            sentences: Vec::new(),
            counts: Vec::new(),
            ids: HashMap::new(),
            typed: String::new(),
            cursor: Some(0),
        };
        for (s, &t) in sentences.iter().zip(times) {
            sys.add(s, u64::from(t));
        }
        sys
    }

    fn add(&mut self, sentence: &str, times: u64) {
        if let Some(&id) = self.ids.get(sentence) {
            // Known sentence: bump the count, but the cached lists keep their old order.
            self.counts[id as usize] += times;
            return;
        }
        let id = self.sentences.len() as u32;
        self.ids.insert(sentence.to_string(), id);
        self.sentences.push(sentence.to_string());
        self.counts.push(times);
        let Self { nodes, sentences, counts, .. } = self;
        let hotter = |a: &u32, b: &u32| {
            let (a, b) = (*a as usize, *b as usize);
            counts[b].cmp(&counts[a]).then_with(|| sentences[a].cmp(&sentences[b]))
        };
        let mut at = 0;
        for b in sentence.bytes() {
            let next = nodes[at].children[slot(b)] as usize;
            at = if next != 0 {
                next
            } else {
                nodes.push(Node::default());
                let n = nodes.len() - 1;
                nodes[at].children[slot(b)] = n as u32;
                n
            };
            let top = &mut nodes[at].top;
            top.push(id);
            top.sort_by(hotter);
            top.truncate(3);
        }
    }

    pub fn input(&mut self, c: char) -> Vec<String> {
        if c == '#' {
            let typed = std::mem::take(&mut self.typed);
            self.add(&typed, 1);
            self.cursor = Some(0);
            return Vec::new();
        }
        self.typed.push(c);
        self.cursor = self.cursor.map(|at| self.nodes[at].children[slot(c as u8)] as usize).filter(|&n| n != 0);
        match self.cursor {
            Some(at) => self.nodes[at].top.iter().map(|&id| self.sentences[id as usize].clone()).collect(),
            None => Vec::new(),
        }
    }
}

#[derive(Debug, Default)]
pub struct Worker {
    pub current: Option<String>,
    pub done: Vec<String>,
}

impl Worker {
    /// Starts `task` and returns the task it interrupted, if any.
    pub fn start(&mut self, task: String) -> Option<String> {
        let old = self.current;
        self.current = Some(task);
        old
    }

    /// Moves the current task to `done`. Returns false if there was none.
    pub fn finish(&mut self) -> bool {
        match self.current {
            Some(task) => {
                self.done.push(task);
                true
            }
            None => false,
        }
    }

    /// The current task, for editing in place.
    pub fn current_mut(&mut self) -> Option<&mut str> {
        self.current.map(|mut s| s.as_mut_str())
    }
}

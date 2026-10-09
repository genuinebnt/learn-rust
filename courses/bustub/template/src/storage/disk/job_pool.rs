//! A small pool of worker threads that run submitted jobs.

use std::collections::VecDeque;
use std::sync::{Arc, Condvar, Mutex};
use std::thread::{self, JoinHandle};

type Job = Box<dyn FnOnce() + Send + 'static>;

struct Shared {
    state: Mutex<State>,
    work: Condvar,
}

struct State {
    queue: VecDeque<Job>,
    stopping: bool,
}

pub struct JobPool {
    shared: Arc<Shared>,
    workers: Vec<JoinHandle<()>>,
}

impl JobPool {
    pub fn new(workers: usize) -> JobPool {
        let shared = Arc::new(Shared { state: Mutex::new(State { queue: VecDeque::new(), stopping: false }), work: Condvar::new() });
        let workers = (0..workers.max(1))
            .map(|_| {
                let shared = Arc::clone(&shared);
                thread::spawn(move || loop {
                    let job = {
                        let mut st = shared.state.lock().unwrap();
                        loop {
                            if st.stopping {
                                break None;
                            }
                            if let Some(job) = st.queue.pop_front() {
                                break Some(job);
                            }
                            st = shared.work.wait(st).unwrap();
                        }
                    };
                    match job {
                        Some(job) => job(),
                        None => return,
                    }
                })
            })
            .collect();
        JobPool { shared, workers }
    }

    /// Queues a job; false if the pool has been shut down.
    pub fn submit(&self, job: impl FnOnce() + Send + 'static) -> bool {
        let mut st = self.shared.state.lock().unwrap();
        if st.stopping {
            return false;
        }
        st.queue.push_back(Box::new(job));
        self.shared.work.notify_one();
        true
    }

    /// Waits for every accepted job to run, then stops the workers.
    pub fn shutdown(&mut self) {
        self.shared.state.lock().unwrap().stopping = true;
        self.shared.work.notify_all();
        for w in self.workers.drain(..) {
            let _ = w.join();
        }
    }
}

impl Drop for JobPool {
    fn drop(&mut self) {
        self.shutdown();
    }
}

#[derive(Debug, PartialEq)]
pub enum Job {
    Queued(String),
    Running(String),
    Done(String),
}

pub fn advance(job: &mut Job) {
    // Take the job out, leaving a placeholder that doesn't allocate, then write the next state.
    *job = match std::mem::replace(job, Job::Done(String::new())) {
        Job::Queued(name) => Job::Running(name),
        Job::Running(name) => Job::Done(name),
        done => done,
    };
}

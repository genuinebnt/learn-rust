#[derive(Debug, PartialEq)]
pub enum Job {
    Queued(String),
    Running(String),
    Done(String),
}

pub fn advance(job: &mut Job) {
    *job = match std::mem::replace(job, Job::Done(String::new())) {
        Job::Queued(name) => Job::Running(name),
        Job::Running(name) => Job::Done(name),
        Job::Done(name) => Job::Queued(name),
    };
}

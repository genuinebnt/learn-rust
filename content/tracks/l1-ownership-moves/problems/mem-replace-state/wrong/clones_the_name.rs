#[derive(Debug, PartialEq)]
pub enum Job {
    Queued(String),
    Running(String),
    Done(String),
}

pub fn advance(job: &mut Job) {
    *job = match job {
        Job::Queued(name) => Job::Running(name.clone()),
        Job::Running(name) => Job::Done(name.clone()),
        Job::Done(name) => Job::Done(name.clone()),
    };
}

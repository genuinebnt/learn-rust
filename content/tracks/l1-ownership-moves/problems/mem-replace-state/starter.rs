#[derive(Debug, PartialEq)]
pub enum Job {
    Queued(String),
    Running(String),
    Done(String),
}

pub fn advance(job: &mut Job) {
    todo!()
}

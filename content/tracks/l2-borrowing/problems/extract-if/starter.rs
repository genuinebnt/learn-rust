#[derive(Debug, PartialEq)]
pub struct Job {
    pub name: &'static str,
    pub deadline: u64,
}

pub fn take_expired(jobs: &mut Vec<Job>, now: u64) -> Vec<Job> {
    todo!()
}

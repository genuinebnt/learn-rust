#[derive(Debug, PartialEq)]
pub struct Job {
    pub name: &'static str,
    pub deadline: u64,
}

pub fn take_expired(jobs: &mut Vec<Job>, now: u64) -> Vec<Job> {
    let mut gone = Vec::new();
    let mut i = 0;
    while i < jobs.len() {
        if jobs[i].deadline < now {
            gone.push(jobs.remove(i));
        } else {
            i += 1;
        }
    }
    gone
}

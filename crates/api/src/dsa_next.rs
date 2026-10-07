//! Which DSA problem comes next. The owner can start anywhere: the next problem is the one after it in the track, then
//! the tracks below it in order, then back round to whatever is left above. Problems already done are skipped. Picking
//! another track (or starting any problem) moves the starting point, and the same rule applies from there.

/// A problem in the catalog's order (track by track, in each track's order), and whether it's done.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Entry<'a> {
    pub id: &'a str,
    pub done: bool,
}

/// The next `count` problems to do, starting at `start` (a problem id: the one just started, or the first problem of
/// the track the owner picked). Unknown or no `start` means the top of the list.
pub fn next_up<'a>(list: &[Entry<'a>], start: Option<&str>, count: usize) -> Vec<&'a str> {
    let from = start.and_then(|s| list.iter().position(|e| e.id == s)).unwrap_or(0);
    list.iter().cycle().skip(from).take(list.len()).filter(|e| !e.done).take(count).map(|e| e.id).collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn list(spec: &[(&'static str, bool)]) -> Vec<Entry<'static>> {
        spec.iter().map(|&(id, done)| Entry { id, done }).collect()
    }

    #[test]
    fn follows_the_track_then_the_tracks_below() {
        let l = list(&[("a1", false), ("a2", false), ("b1", false), ("b2", false), ("c1", false)]);
        assert_eq!(next_up(&l, Some("b1"), 3), ["b1", "b2", "c1"]);
        assert_eq!(next_up(&l, None, 2), ["a1", "a2"]);
    }

    #[test]
    fn comes_back_round_to_what_was_left_above() {
        let l = list(&[("a1", false), ("a2", false), ("b1", false), ("c1", false)]);
        assert_eq!(next_up(&l, Some("c1"), 4), ["c1", "a1", "a2", "b1"]);
    }

    #[test]
    fn skips_done_problems_and_whole_finished_tracks() {
        let l = list(&[("a1", true), ("a2", true), ("b1", false), ("b2", true), ("c1", false), ("d1", false)]);
        // Starting in a finished track goes straight to the first thing left below it.
        assert_eq!(next_up(&l, Some("a1"), 3), ["b1", "c1", "d1"]);
        // Starting in b: b2 is done, so on to c, then round to b1.
        assert_eq!(next_up(&l, Some("b2"), 3), ["c1", "d1", "b1"]);
    }

    #[test]
    fn nothing_left_or_an_unknown_start() {
        let all_done = list(&[("a1", true), ("b1", true)]);
        assert!(next_up(&all_done, Some("a1"), 3).is_empty());
        assert!(next_up(&[], None, 3).is_empty());
        let l = list(&[("a1", false), ("b1", false)]);
        assert_eq!(next_up(&l, Some("gone"), 1), ["a1"]);
        assert_eq!(next_up(&l, Some("b1"), 0), Vec::<&str>::new());
    }
}

//! The write-ahead log in memory and on disk. Records are appended to a buffer and get their **LSN** (log sequence number: here the byte
//! offset where the record starts in the whole log); `flush` makes the buffer durable. A crash loses the buffer and nothing else.

use std::io;
use std::sync::{Arc, Mutex};

use super::log_io::LogIo;
use super::log_record::{parse_log, LogRecord};

pub type Lsn = u64;

pub struct LogManager {
    // @begin 4c-02
    io: Arc<dyn LogIo>,
    state: Mutex<State>,
    //~ // TODO(4c-02): your fields: the log device, the records not yet written, where the durable part ends
    // @end
}

// @begin 4c-02
struct State {
    /// Serialized records appended and not yet durable.
    buffer: Vec<u8>,
    /// The log is durable up to (not including) this offset.
    durable: u64,
}
//~ // TODO(4c-02): helper types of your own
// @end

impl LogManager {
    /// A log manager over `io`. If the log already holds records (the system is starting after a crash) it continues after them: the
    /// next record goes where the last intact one ends, and a torn tail (a record cut off by the crash) is cut away first so that new
    /// records never follow garbage.
    pub fn new(io: Arc<dyn LogIo>) -> io::Result<LogManager> {
        // @begin 4c-02
        let bytes = io.read_all()?;
        let (_, intact) = parse_log(&bytes);
        if intact < bytes.len() {
            io.truncate(intact as u64)?;
        }
        Ok(LogManager { io, state: Mutex::new(State { buffer: Vec::new(), durable: intact as u64 }) })
        //~ todo!("4c-02: read the durable log, find where the last intact record ends (parse_log), truncate a torn tail, and start there")
        // @end
    }

    /// Adds a record to the log buffer and returns its LSN. Not durable until a flush.
    pub fn append(&self, record: &LogRecord) -> Lsn {
        // @begin 4c-02
        let mut state = self.state.lock().unwrap();
        let lsn = state.durable + state.buffer.len() as u64;
        state.buffer.extend_from_slice(&record.serialize());
        lsn
        //~ todo!("4c-02: the record's bytes go to the end of the buffer; its LSN is the offset where it starts in the whole log")
        // @end
    }

    /// Writes everything appended so far to the log device.
    pub fn flush(&self) -> io::Result<()> {
        // @begin 4c-02
        let mut state = self.state.lock().unwrap();
        if state.buffer.is_empty() {
            return Ok(());
        }
        self.io.append(&state.buffer)?;
        state.durable += state.buffer.len() as u64;
        state.buffer.clear();
        Ok(())
        //~ todo!("4c-02: append the buffer to the device, move the durable end, empty the buffer; nothing to do if it is empty")
        // @end
    }

    /// Makes sure the record that starts at `lsn` is durable (a no-op if it already is).
    pub fn flush_to(&self, lsn: Lsn) -> io::Result<()> {
        // @begin 4c-02
        if lsn < self.flushed_lsn() {
            return Ok(());
        }
        self.flush()
        //~ todo!("4c-02: if the record at lsn is not durable yet, flush")
        // @end
    }

    /// Every record that starts before this offset is durable.
    pub fn flushed_lsn(&self) -> Lsn {
        // @begin 4c-02
        self.state.lock().unwrap().durable
        //~ todo!("4c-02: where the durable part of the log ends")
        // @end
    }

    /// Where the next record will start (the buffered ones included).
    pub fn end_lsn(&self) -> Lsn {
        // @begin 4c-02
        let state = self.state.lock().unwrap();
        state.durable + state.buffer.len() as u64
        //~ todo!("4c-02: durable end plus what is buffered")
        // @end
    }

    /// The durable records, in order, each with its LSN. A torn tail is not part of the log. (This is what recovery reads.)
    pub fn records(&self) -> io::Result<Vec<(Lsn, LogRecord)>> {
        // @begin 4c-02
        Ok(parse_log(&self.io.read_all()?).0)
        //~ todo!("4c-02: read the whole log from the device and parse it (parse_log): the records that survived, with their LSNs")
        // @end
    }
}

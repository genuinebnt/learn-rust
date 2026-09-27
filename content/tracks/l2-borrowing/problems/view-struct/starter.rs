pub struct Document {
    pub title: String,
    pub body: String,
    pub tags: Vec<String>,
}

pub struct Header<'a> {
    pub title: &'a mut String,
    pub tags: &'a mut Vec<String>,
}

impl Document {
    pub fn header(&mut self) -> Header<'_> {
        todo!()
    }
}

impl Header<'_> {
    pub fn retitle(&mut self, new_title: &str) {
        todo!()
    }
}

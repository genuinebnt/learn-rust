use std::marker::PhantomData;

#[derive(Debug, PartialEq)]
pub struct Request {
    pub url: String,
    pub headers: Vec<(String, String)>,
    pub timeout_ms: u64,
}

#[derive(Debug, PartialEq)]
pub enum UrlError {
    Empty,
    NoScheme,
}

/// The builder's states: before and after it has a URL.
pub struct NoUrl;
pub struct HasUrl;

pub struct RequestBuilder<S> {
    url: String,
    headers: Vec<(String, String)>,
    timeout_ms: u64,
    state: PhantomData<S>,
}

impl RequestBuilder<NoUrl> {
    /// No URL, no headers, a 30 000 ms timeout.
    pub fn new() -> Self {
        todo!()
    }

    /// The only way to get a builder that can `build`.
    pub fn url(self, url: &str) -> Result<RequestBuilder<HasUrl>, UrlError> {
        todo!()
    }
}

impl<S> RequestBuilder<S> {
    pub fn header(self, key: &str, value: &str) -> Self {
        todo!()
    }

    pub fn timeout_ms(self, ms: u64) -> Self {
        todo!()
    }
}

impl RequestBuilder<HasUrl> {
    pub fn build(self) -> Request {
        todo!()
    }
}

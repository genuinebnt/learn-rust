//! anneal's AI layer, on [rig](https://rig.rs) (`rig-core`): a streaming chat call and text embeddings, with the
//! provider chosen at startup from the environment. Keys never leave the server.
//!
//! | Variable | Meaning |
//! |---|---|
//! | `ANNEAL_AI_PROVIDER` | `gemini`, `openai` or `anthropic`; default: the first of those whose key is set |
//! | `GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` | the provider's key |
//! | `ANNEAL_AI_MODEL` | chat model; default per provider (see [`Provider::default_model`]) |
//! | `ANNEAL_AI_EMBED_PROVIDER` | `gemini`, `openai` or `none`; default: the chat provider if it has embeddings, else another with a key |
//! | `ANNEAL_AI_EMBED_MODEL` | embedding model; default per provider |
//!
//! With no key at all, [`Ai::from_env`] returns `None` and the app runs without AI.

use anyhow::{Context, anyhow, bail};
use futures_util::StreamExt;
use futures_util::stream::BoxStream;
use rig_core::client::{CompletionClient, EmbeddingsClient, ProviderClient};
use rig_core::completion::{CompletionModel, Document, Message};
use rig_core::embeddings::EmbeddingModel;
use rig_core::providers::{anthropic, gemini, openai};
use rig_core::streaming::StreamedAssistantContent;
use serde::Serialize;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum Provider {
    Gemini,
    #[serde(rename = "openai")]
    OpenAi,
    Anthropic,
}

impl Provider {
    const ALL: [Provider; 3] = [Provider::Gemini, Provider::OpenAi, Provider::Anthropic];

    fn parse(s: &str) -> anyhow::Result<Self> {
        match s.to_ascii_lowercase().as_str() {
            "gemini" => Ok(Provider::Gemini),
            "openai" => Ok(Provider::OpenAi),
            "anthropic" | "claude" => Ok(Provider::Anthropic),
            other => bail!("unknown AI provider {other:?}; use gemini, openai or anthropic"),
        }
    }

    fn key_env(self) -> &'static str {
        match self {
            Provider::Gemini => "GEMINI_API_KEY",
            Provider::OpenAi => "OPENAI_API_KEY",
            Provider::Anthropic => "ANTHROPIC_API_KEY",
        }
    }

    fn has_key(self) -> bool {
        std::env::var(self.key_env()).is_ok_and(|k| !k.trim().is_empty())
    }

    /// The chat model used unless `ANNEAL_AI_MODEL` says otherwise.
    pub fn default_model(self) -> &'static str {
        match self {
            Provider::Gemini => gemini::completion::GEMINI_2_5_FLASH,
            Provider::OpenAi => "gpt-5.5",
            Provider::Anthropic => "claude-sonnet-4-6",
        }
    }

    fn default_embed_model(self) -> Option<&'static str> {
        match self {
            Provider::Gemini => Some(gemini::embedding::EMBEDDING_001),
            Provider::OpenAi => Some(openai::embedding::TEXT_EMBEDDING_3_SMALL),
            // Anthropic has no embeddings API.
            Provider::Anthropic => None,
        }
    }
}

/// What's configured, for the status endpoint and the UI's provider badge.
#[derive(Debug, Clone, Serialize)]
pub struct Info {
    pub provider: Provider,
    pub model: String,
    /// `provider/model` for embeddings, or `None` when no embedding provider is available.
    pub embeddings: Option<String>,
}

enum Chat {
    Gemini(gemini::Client),
    OpenAi(openai::Client),
    Anthropic(anthropic::Client),
}

enum Embed {
    Gemini(gemini::Client),
    OpenAi(openai::Client),
}

pub struct Ai {
    chat: Chat,
    embed: Option<(Embed, String)>,
    pub info: Info,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Role {
    User,
    Assistant,
}

/// One completion: instructions, the conversation so far, the new question, and retrieved context.
#[derive(Debug, Clone)]
pub struct Request {
    pub system: String,
    pub history: Vec<(Role, String)>,
    pub prompt: String,
    /// `(id, text)` documents the model should ground its answer in.
    pub context: Vec<(String, String)>,
    pub max_tokens: u64,
}

impl Ai {
    /// Reads the configuration from the environment. `Ok(None)` when no provider key is set.
    pub fn from_env() -> anyhow::Result<Option<Ai>> {
        let var = |k: &str| std::env::var(k).ok().filter(|v| !v.trim().is_empty());
        let provider = match var("ANNEAL_AI_PROVIDER") {
            Some(p) => {
                let p = Provider::parse(&p)?;
                if !p.has_key() {
                    bail!("ANNEAL_AI_PROVIDER is {p:?} but {} is not set", p.key_env());
                }
                p
            }
            None => match Provider::ALL.into_iter().find(|p| p.has_key()) {
                Some(p) => p,
                None => return Ok(None),
            },
        };
        let model = var("ANNEAL_AI_MODEL").unwrap_or_else(|| provider.default_model().to_owned());
        let chat = match provider {
            Provider::Gemini => Chat::Gemini(gemini::Client::from_env().context("gemini client")?),
            Provider::OpenAi => Chat::OpenAi(openai::Client::from_env().context("openai client")?),
            Provider::Anthropic => Chat::Anthropic(anthropic::Client::from_env().context("anthropic client")?),
        };

        let embed_provider = match var("ANNEAL_AI_EMBED_PROVIDER").as_deref() {
            Some("none") => None,
            Some(p) => Some(Provider::parse(p)?),
            None if provider.default_embed_model().is_some() => Some(provider),
            None => Provider::ALL.into_iter().find(|p| p.default_embed_model().is_some() && p.has_key()),
        };
        let embed = match embed_provider {
            None => None,
            Some(p) => {
                let model = match var("ANNEAL_AI_EMBED_MODEL") {
                    Some(m) => m,
                    None => p.default_embed_model().ok_or_else(|| anyhow!("{p:?} has no embeddings API"))?.to_owned(),
                };
                let client = match p {
                    Provider::Gemini => Embed::Gemini(gemini::Client::from_env().context("gemini client")?),
                    Provider::OpenAi => Embed::OpenAi(openai::Client::from_env().context("openai client")?),
                    Provider::Anthropic => bail!("anthropic has no embeddings API; set ANNEAL_AI_EMBED_PROVIDER"),
                };
                Some((client, model, p))
            }
        };
        let info = Info {
            provider,
            model: model.clone(),
            embeddings: embed.as_ref().map(|(_, m, p)| format!("{}/{m}", serde_label(*p))),
        };
        Ok(Some(Ai { chat, embed: embed.map(|(c, m, _)| (c, m)), info }))
    }

    /// Streams the answer as text chunks.
    pub async fn stream(&self, req: Request) -> anyhow::Result<BoxStream<'static, anyhow::Result<String>>> {
        let model = &self.info.model;
        match &self.chat {
            Chat::Gemini(c) => stream_with(c.completion_model(model), req).await,
            Chat::OpenAi(c) => stream_with(c.completion_model(model), req).await,
            Chat::Anthropic(c) => stream_with(c.completion_model(model), req).await,
        }
    }

    /// The whole answer at once, for background jobs like the patterns report.
    pub async fn complete(&self, req: Request) -> anyhow::Result<String> {
        let mut out = String::new();
        let mut chunks = self.stream(req).await?;
        while let Some(chunk) = chunks.next().await {
            out.push_str(&chunk?);
        }
        Ok(out)
    }

    /// Whether [`Ai::embed`] is available.
    pub fn can_embed(&self) -> bool {
        self.embed.is_some()
    }

    /// Embeds each text; vectors come back in the same order.
    pub async fn embed(&self, texts: Vec<String>) -> anyhow::Result<Vec<Vec<f32>>> {
        let Some((client, model)) = &self.embed else { bail!("no embedding provider is configured") };
        match client {
            Embed::Gemini(c) => embed_with(c.embedding_model(model), texts).await,
            Embed::OpenAi(c) => embed_with(c.embedding_model(model), texts).await,
        }
    }
}

fn serde_label(p: Provider) -> &'static str {
    match p {
        Provider::Gemini => "gemini",
        Provider::OpenAi => "openai",
        Provider::Anthropic => "anthropic",
    }
}

async fn stream_with<M>(model: M, req: Request) -> anyhow::Result<BoxStream<'static, anyhow::Result<String>>>
where
    M: CompletionModel + Clone + 'static,
{
    let history = req.history.into_iter().map(|(role, text)| match role {
        Role::User => Message::user(text),
        Role::Assistant => Message::assistant(text),
    });
    let documents = req.context.into_iter().map(|(id, text)| Document { id, text, additional_props: Default::default() });
    let request = model
        .completion_request(Message::user(req.prompt))
        .preamble(req.system)
        .messages(history)
        .documents(documents)
        .max_tokens(req.max_tokens)
        .build();
    let response = model.stream(request).await.context("starting the model's stream")?;
    Ok(response
        .filter_map(|item| async move {
            match item {
                Ok(StreamedAssistantContent::Text(t)) => Some(Ok(t.text)),
                Ok(_) => None,
                Err(e) => Some(Err(anyhow!(e).context("the model's stream failed"))),
            }
        })
        .boxed())
}

async fn embed_with<M: EmbeddingModel>(model: M, texts: Vec<String>) -> anyhow::Result<Vec<Vec<f32>>> {
    let mut out = Vec::with_capacity(texts.len());
    for chunk in texts.chunks(M::MAX_DOCUMENTS.max(1)) {
        let embeddings = model.embed_texts(chunk.to_vec()).await.context("embedding")?;
        out.extend(embeddings.into_iter().map(|e| e.vec.into_iter().map(|x| x as f32).collect::<Vec<f32>>()));
    }
    Ok(out)
}

/// Cosine similarity of two vectors of the same length (0 when either is all zeros).
pub fn cosine(a: &[f32], b: &[f32]) -> f32 {
    let (mut dot, mut na, mut nb) = (0f32, 0f32, 0f32);
    for (x, y) in a.iter().zip(b) {
        dot += x * y;
        na += x * x;
        nb += y * y;
    }
    if na == 0.0 || nb == 0.0 { 0.0 } else { dot / (na.sqrt() * nb.sqrt()) }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn cosine_of_parallel_orthogonal_and_zero_vectors() {
        assert!((cosine(&[1.0, 2.0], &[2.0, 4.0]) - 1.0).abs() < 1e-6);
        assert!(cosine(&[1.0, 0.0], &[0.0, 1.0]).abs() < 1e-6);
        assert_eq!(cosine(&[0.0, 0.0], &[1.0, 1.0]), 0.0);
    }

    #[test]
    fn provider_names_parse() {
        assert_eq!(Provider::parse("Gemini").unwrap(), Provider::Gemini);
        assert_eq!(Provider::parse("claude").unwrap(), Provider::Anthropic);
        assert!(Provider::parse("llama").is_err());
    }
}

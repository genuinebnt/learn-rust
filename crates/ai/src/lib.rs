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
use rig_core::client::{CompletionClient, EmbeddingsClient};
use rig_core::completion::{CompletionModel, Document, Message};
use rig_core::embeddings::EmbeddingModel;
use rig_core::providers::{anthropic, gemini, openai};
use rig_core::streaming::StreamedAssistantContent;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Provider {
    Gemini,
    #[serde(rename = "openai")]
    OpenAi,
    Anthropic,
}

impl Provider {
    const ALL: [Provider; 3] = [Provider::Gemini, Provider::OpenAi, Provider::Anthropic];

    pub fn parse(s: &str) -> anyhow::Result<Self> {
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
    /// The keys in use, so error messages can be scrubbed of them (Gemini's key travels in the URL).
    secrets: Vec<String>,
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

/// Everything needed to build an [`Ai`]: from the app's settings, or from the environment.
#[derive(Clone)]
pub struct Config {
    pub provider: Provider,
    pub api_key: String,
    /// The chat model; `None` for the provider's default.
    pub model: Option<String>,
    /// Where embeddings come from; `None` for no embeddings (similarity falls back to tags).
    pub embed: Option<EmbedConfig>,
}

#[derive(Clone)]
pub struct EmbedConfig {
    pub provider: Provider,
    pub api_key: String,
    pub model: Option<String>,
}

impl std::fmt::Debug for Config {
    // Never print keys.
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("Config").field("provider", &self.provider).field("model", &self.model).finish_non_exhaustive()
    }
}

fn env_var(k: &str) -> Option<String> {
    std::env::var(k).ok().filter(|v| !v.trim().is_empty())
}

impl Provider {
    fn env_key(self) -> Option<String> {
        env_var(self.key_env())
    }
}

impl Config {
    /// The configuration in the environment (see the module docs), or `None` when no key is set.
    pub fn from_env() -> anyhow::Result<Option<Config>> {
        let provider = match env_var("ANNEAL_AI_PROVIDER") {
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
        let embed_provider = match env_var("ANNEAL_AI_EMBED_PROVIDER").as_deref() {
            Some("none") => None,
            Some(p) => Some(Provider::parse(p)?),
            None if provider.default_embed_model().is_some() => Some(provider),
            None => Provider::ALL.into_iter().find(|p| p.default_embed_model().is_some() && p.has_key()),
        };
        let embed = match embed_provider {
            None => None,
            Some(p) => Some(EmbedConfig {
                provider: p,
                api_key: p.env_key().ok_or_else(|| anyhow!("{} is not set for embeddings", p.key_env()))?,
                model: env_var("ANNEAL_AI_EMBED_MODEL"),
            }),
        };
        Ok(Some(Config {
            provider,
            api_key: provider.env_key().expect("checked above"),
            model: env_var("ANNEAL_AI_MODEL"),
            embed,
        }))
    }

    /// A configuration for one provider and key: embeddings from the same provider when it has them, otherwise from
    /// the environment's Gemini or OpenAI key if there is one.
    pub fn single(provider: Provider, api_key: String, model: Option<String>) -> Config {
        let embed = if provider.default_embed_model().is_some() {
            Some(EmbedConfig { provider, api_key: api_key.clone(), model: None })
        } else {
            [Provider::Gemini, Provider::OpenAi]
                .into_iter()
                .find_map(|p| p.env_key().map(|k| EmbedConfig { provider: p, api_key: k, model: None }))
        };
        Config { provider, api_key, model, embed }
    }
}

impl Ai {
    /// The assistant configured in the environment, or `None` when no key is set.
    pub fn from_env() -> anyhow::Result<Option<Ai>> {
        Config::from_env()?.map(Ai::new).transpose()
    }

    pub fn new(cfg: Config) -> anyhow::Result<Ai> {
        let model = cfg.model.clone().unwrap_or_else(|| cfg.provider.default_model().to_owned());
        let key = cfg.api_key.clone();
        let mut secrets = vec![cfg.api_key.clone()];
        if let Some(e) = &cfg.embed {
            secrets.push(e.api_key.clone());
        }
        let chat = match cfg.provider {
            Provider::Gemini => Chat::Gemini(gemini::Client::new(key).context("gemini client")?),
            Provider::OpenAi => Chat::OpenAi(openai::Client::new(key).context("openai client")?),
            Provider::Anthropic => Chat::Anthropic(anthropic::Client::new(key).context("anthropic client")?),
        };
        let embed = match cfg.embed {
            None => None,
            Some(e) => {
                let model = match e.model {
                    Some(m) => m,
                    None => e.provider.default_embed_model().ok_or_else(|| anyhow!("{:?} has no embeddings API", e.provider))?.to_owned(),
                };
                let client = match e.provider {
                    Provider::Gemini => Embed::Gemini(gemini::Client::new(e.api_key).context("gemini client")?),
                    Provider::OpenAi => Embed::OpenAi(openai::Client::new(e.api_key).context("openai client")?),
                    Provider::Anthropic => bail!("anthropic has no embeddings API"),
                };
                Some((client, model, e.provider))
            }
        };
        let info = Info {
            provider: cfg.provider,
            model: model.clone(),
            embeddings: embed.as_ref().map(|(_, m, p)| format!("{}/{m}", serde_label(*p))),
        };
        Ok(Ai { chat, embed: embed.map(|(c, m, _)| (c, m)), secrets, info })
    }

    /// `text` with any key in use replaced by `••••`. Use it on every error that leaves this crate.
    pub fn redact(&self, text: &str) -> String {
        self.secrets.iter().filter(|k| k.len() >= 8).fold(text.to_owned(), |t, k| t.replace(k.as_str(), "••••"))
    }

    /// A tiny request to check the key and model work, used before saving a key from the settings.
    pub async fn check(&self) -> anyhow::Result<()> {
        let reply = self
            .complete(Request {
                system: "Reply with the single word OK.".into(),
                history: Vec::new(),
                prompt: "Say OK.".into(),
                context: Vec::new(),
                max_tokens: 16,
            })
            .await?;
        if reply.trim().is_empty() {
            bail!("the model returned an empty answer");
        }
        if self.can_embed() {
            self.embed(vec!["ok".into()]).await.context("embeddings")?;
        }
        Ok(())
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

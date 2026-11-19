//! The error of the schema to Rust renderer.

use std::error::Error;
use std::fmt;
use std::io;
use std::path::PathBuf;

/// Everything that can go wrong while generating the Rust types of the models.
#[derive(Debug)]
pub enum CodegenError {
    /// A file could not be read or written.
    Io {
        /// The file concerned.
        path: PathBuf,
        /// The underlying error.
        source: io::Error,
    },
    /// The schema bundle is not valid JSON, or not a JSON Schema.
    Schema(serde_json::Error),
    /// The schema bundle has a shape the renderer does not accept.
    Invalid(String),
    /// The type generator refused a schema.
    Generation(String),
    /// The generated code does not parse as Rust.
    Syntax(syn::Error),
}

impl fmt::Display for CodegenError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Io { path, source } => write!(formatter, "Cannot access {}: {source}.", path.display()),
            Self::Schema(error) => write!(formatter, "The schema bundle is not readable: {error}."),
            Self::Invalid(reason) => write!(formatter, "The schema bundle is invalid: {reason}."),
            Self::Generation(reason) => write!(formatter, "The types cannot be generated: {reason}."),
            Self::Syntax(error) => write!(formatter, "The generated code is not valid Rust: {error}."),
        }
    }
}

impl Error for CodegenError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            Self::Io { source, .. } => Some(source),
            Self::Schema(error) => Some(error),
            Self::Syntax(error) => Some(error),
            Self::Invalid(_) | Self::Generation(_) => None,
        }
    }
}

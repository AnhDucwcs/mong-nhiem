//! Bimodal Emission Protocol and Parser.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum CommClass {
    Inform,
    Query,
    Alert,
}

impl CommClass {
    pub fn as_str(&self) -> &'static str {
        match self {
            CommClass::Inform => "INFORM",
            CommClass::Query => "QUERY",
            CommClass::Alert => "ALERT",
        }
    }

    pub fn from_str_lossy(s: &str) -> Self {
        match s.trim().to_uppercase().as_str() {
            "QUERY" => CommClass::Query,
            "ALERT" => CommClass::Alert,
            _ => CommClass::Inform,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct BimodalEmission {
    pub action_verb: String,
    pub action_params: HashMap<String, String>,
    pub comm_class: CommClass,
    pub comm_message: String,
}

pub struct BimodalParser;

impl BimodalParser {
    pub fn parse(text: &str) -> Result<BimodalEmission, String> {
        let mut action_line = None;
        let mut comm_line = None;

        for line in text.lines() {
            let trimmed = line.trim();
            if trimmed.starts_with("ACTION:") {
                action_line = Some(trimmed);
            } else if trimmed.starts_with("COMMUNICATE") {
                comm_line = Some(trimmed);
            }
        }

        let action_raw = action_line.ok_or_else(|| "Missing ACTION line in emission".to_string())?;
        let comm_raw = comm_line.ok_or_else(|| "Missing COMMUNICATE line in emission".to_string())?;

        // 1. Parse Action
        let action_body = action_raw.strip_prefix("ACTION:").unwrap().trim();
        let mut parts = action_body.split_whitespace();
        let verb = parts.next().unwrap_or("NOMINAL_STEP").to_string();

        let mut params = HashMap::new();
        for token in parts {
            if let Some((k, v)) = token.split_once('=') {
                params.insert(k.trim().to_string(), v.trim().to_string());
            }
        }

        // 2. Parse Communicate [CLASS]: "Message"
        let comm_rest = comm_raw.strip_prefix("COMMUNICATE").unwrap().trim();
        let comm_class;
        let mut message_part = comm_rest;

        if comm_rest.starts_with('[') {
            if let Some(close_idx) = comm_rest.find(']') {
                let class_str = &comm_rest[1..close_idx];
                comm_class = CommClass::from_str_lossy(class_str);
                message_part = comm_rest[close_idx + 1..].trim();
            } else {
                comm_class = CommClass::Inform;
            }
        } else {
            comm_class = CommClass::Inform;
        }

        if message_part.starts_with(':') {
            message_part = message_part[1..].trim();
        }

        let message = message_part.trim_matches('"').trim_matches('\'').to_string();

        Ok(BimodalEmission {
            action_verb: verb,
            action_params: params,
            comm_class,
            comm_message: message,
        })
    }
}

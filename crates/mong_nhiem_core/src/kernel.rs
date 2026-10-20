//! Authoritative Cognitive Kernel in Rust.

use std::collections::HashMap;
use serde::{Deserialize, Serialize};

use crate::bimodal::{BimodalParser, CommClass};
use crate::state::ContinuousStateEngine;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StepResult {
    pub action_verb: String,
    pub action_params: HashMap<String, String>,
    pub comm_class: String,
    pub comm_message: String,
    pub tick: u64,
    pub delta_time: f64,
    pub state_snapshot: HashMap<String, f64>,
    pub fired_invariants: Vec<String>,
}

#[derive(Debug)]
pub struct MongNhiemKernel {
    pub state_engine: ContinuousStateEngine,
    pub current_tick: u64,
}

impl Default for MongNhiemKernel {
    fn default() -> Self {
        Self::new()
    }
}

impl MongNhiemKernel {
    pub fn new() -> Self {
        Self {
            state_engine: ContinuousStateEngine::new(),
            current_tick: 0,
        }
    }

    pub fn tick(&mut self, stimulus: &str, delta_time: f64) -> StepResult {
        self.current_tick += 1;

        // 1. Advance continuous physics / decay
        let fired_invariants = self.state_engine.advance(delta_time);

        // 2. Reflex Interception: If safety invariant violated, override action
        let (action_verb, action_params, comm_class, comm_message) = if let Some(first_fired) = fired_invariants.first() {
            (
                first_fired.clone(),
                HashMap::new(),
                CommClass::Alert,
                format!("Emergency reflex triggered: {}", first_fired),
            )
        } else if !stimulus.is_empty() {
            // Attempt to parse stimulus if formatted as bimodal emission, otherwise emit nominal
            if let Ok(emission) = BimodalParser::parse(stimulus) {
                (
                    emission.action_verb,
                    emission.action_params,
                    emission.comm_class,
                    emission.comm_message,
                )
            } else {
                (
                    "NOMINAL_STEP".to_string(),
                    HashMap::new(),
                    CommClass::Inform,
                    format!("Processed: {}", stimulus),
                )
            }
        } else {
            (
                "IDLE".to_string(),
                HashMap::new(),
                CommClass::Inform,
                "Nominal tick".to_string(),
            )
        };

        StepResult {
            action_verb,
            action_params,
            comm_class: comm_class.as_str().to_string(),
            comm_message,
            tick: self.current_tick,
            delta_time,
            state_snapshot: self.state_engine.get_snapshot(),
            fired_invariants,
        }
    }
}

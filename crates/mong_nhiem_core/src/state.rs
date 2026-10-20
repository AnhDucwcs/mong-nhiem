//! Continuous State Engine and Invariant Triggers in Rust.

use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq)]
pub struct ContinuousVariable {
    pub name: String,
    pub value: f64,
    pub min_val: f64,
    pub max_val: f64,
    pub rate_per_sec: f64,
    pub is_decay: bool,
}

impl ContinuousVariable {
    pub fn new(
        name: impl Into<String>,
        initial_value: f64,
        min_val: f64,
        max_val: f64,
        rate_per_sec: f64,
        is_decay: bool,
    ) -> Self {
        let val = initial_value.clamp(min_val, max_val);
        Self {
            name: name.into(),
            value: val,
            min_val,
            max_val,
            rate_per_sec,
            is_decay,
        }
    }

    pub fn advance(&mut self, delta_time: f64) {
        if delta_time <= 0.0 || self.rate_per_sec == 0.0 {
            return;
        }
        let delta = self.rate_per_sec * delta_time;
        if self.is_decay {
            self.value = (self.value - delta).clamp(self.min_val, self.max_val);
        } else {
            self.value = (self.value + delta).clamp(self.min_val, self.max_val);
        }
    }
}

#[derive(Debug, Clone, PartialEq)]
pub struct InvariantTrigger {
    pub variable_name: String,
    pub threshold: f64,
    pub comparison: String,
    pub trigger_action: String,
}

impl InvariantTrigger {
    pub fn is_violated(&self, current_value: f64) -> bool {
        match self.comparison.as_str() {
            ">=" => current_value >= self.threshold,
            "<=" => current_value <= self.threshold,
            ">" => current_value > self.threshold,
            "<" => current_value < self.threshold,
            "==" => (current_value - self.threshold).abs() < f64::EPSILON,
            "!=" => (current_value - self.threshold).abs() >= f64::EPSILON,
            _ => false,
        }
    }
}

#[derive(Debug, Default, Clone)]
pub struct ContinuousStateEngine {
    variables: HashMap<String, ContinuousVariable>,
    triggers: Vec<InvariantTrigger>,
}

impl ContinuousStateEngine {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn register_variable(
        &mut self,
        name: impl Into<String>,
        initial_value: f64,
        min_val: f64,
        max_val: f64,
        rate_per_sec: f64,
        is_decay: bool,
    ) {
        let name_str = name.into();
        self.variables.insert(
            name_str.clone(),
            ContinuousVariable::new(name_str, initial_value, min_val, max_val, rate_per_sec, is_decay),
        );
    }

    pub fn register_trigger(
        &mut self,
        variable_name: impl Into<String>,
        threshold: f64,
        comparison: impl Into<String>,
        trigger_action: impl Into<String>,
    ) {
        self.triggers.push(InvariantTrigger {
            variable_name: variable_name.into(),
            threshold,
            comparison: comparison.into(),
            trigger_action: trigger_action.into(),
        });
    }

    pub fn get_variable(&self, name: &str) -> Option<f64> {
        self.variables.get(name).map(|v| v.value)
    }

    pub fn set_variable(&mut self, name: &str, value: f64) -> bool {
        if let Some(var) = self.variables.get_mut(name) {
            var.value = value.clamp(var.min_val, var.max_val);
            true
        } else {
            false
        }
    }

    pub fn advance(&mut self, delta_time: f64) -> Vec<String> {
        for var in self.variables.values_mut() {
            var.advance(delta_time);
        }

        let mut fired = Vec::new();
        for trig in &self.triggers {
            if let Some(var) = self.variables.get(&trig.variable_name) {
                if trig.is_violated(var.value) {
                    fired.push(trig.trigger_action.clone());
                }
            }
        }
        fired
    }

    pub fn get_snapshot(&self) -> HashMap<String, f64> {
        self.variables.iter().map(|(k, v)| (k.clone(), v.value)).collect()
    }
}

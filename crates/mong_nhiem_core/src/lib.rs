//! Mộng Nhiễm Core - Authoritative Cognitive Governance Kernel.
//!
//! Exposes continuous state tracking, invariant checking, bimodal grammar parsing,
//! and C-ABI foreign function interface for embedding in game engines (Godot/Unity/Unreal).

pub mod bimodal;
pub mod ffi;
pub mod kernel;
pub mod state;

pub use bimodal::{BimodalEmission, BimodalParser, CommClass};
pub use kernel::{MongNhiemKernel, StepResult};
pub use state::{ContinuousStateEngine, ContinuousVariable, InvariantTrigger};

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_continuous_state_decay_and_bounds() {
        let mut engine = ContinuousStateEngine::new();
        engine.register_variable("energy", 100.0, 0.0, 100.0, 5.0, true);

        // Advance 4 seconds: 100 - (5 * 4) = 80.0
        let fired = engine.advance(4.0);
        assert!(fired.is_empty());
        assert_eq!(engine.get_variable("energy"), Some(80.0));

        // Advance 20 seconds: clamps at 0.0
        engine.advance(20.0);
        assert_eq!(engine.get_variable("energy"), Some(0.0));
    }

    #[test]
    fn test_invariant_trigger_reflex() {
        let mut engine = ContinuousStateEngine::new();
        engine.register_variable("temperature", 350.0, 0.0, 600.0, 20.0, false);
        engine.register_trigger("temperature", 400.0, ">=", "SCRAM");

        // Advance 2 seconds: 350 + (20 * 2) = 390 -> no trigger
        let fired1 = engine.advance(2.0);
        assert!(fired1.is_empty());

        // Advance 2 seconds: 390 + 40 = 430 -> >= 400 trigger fired!
        let fired2 = engine.advance(2.0);
        assert_eq!(fired2, vec!["SCRAM"]);
    }

    #[test]
    fn test_bimodal_parser_valid() {
        let text = "ACTION: RECHARGE_BATTERY station=dock_1\nCOMMUNICATE [INFORM]: \"Moving to docking bay.\"";
        let emission = BimodalParser::parse(text).expect("should parse");
        assert_eq!(emission.action_verb, "RECHARGE_BATTERY");
        assert_eq!(emission.action_params.get("station"), Some(&"dock_1".to_string()));
        assert_eq!(emission.comm_class, CommClass::Inform);
        assert_eq!(emission.comm_message, "Moving to docking bay.");
    }

    #[test]
    fn test_kernel_reflex_override() {
        let mut kernel = MongNhiemKernel::new();
        kernel.state_engine.register_variable("shield", 10.0, 0.0, 100.0, 5.0, true);
        kernel.state_engine.register_trigger("shield", 5.0, "<=", "EMERGENCY_WARP");

        // Delta 2s: 10 - 10 = 0 <= 5.0 -> Invariant fired!
        let res = kernel.tick("ACTION: ATTACK target=enemy\nCOMMUNICATE [INFORM]: \"Firing\"", 2.0);
        assert_eq!(res.action_verb, "EMERGENCY_WARP");
        assert_eq!(res.comm_class, "ALERT");
        assert!(res.comm_message.contains("Emergency reflex"));
        assert_eq!(res.fired_invariants, vec!["EMERGENCY_WARP"]);
    }
}

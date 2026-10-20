//! Foreign Function Interface (C-ABI) for C, C++, C# (Unity), and Godot.

use std::ffi::{CStr, CString};
use std::os::raw::{c_char, c_double, c_int, c_ulonglong};

use crate::kernel::MongNhiemKernel;

#[repr(C)]
pub struct FfiStepResult {
    pub action_verb: *mut c_char,
    pub comm_class: *mut c_char,
    pub comm_message: *mut c_char,
    pub tick: c_ulonglong,
    pub delta_time: c_double,
    pub state_json: *mut c_char,
    pub has_fired_invariants: c_int,
}

#[no_mangle]
pub extern "C" fn mong_nhiem_version() -> *const c_char {
    static VERSION: &[u8] = b"0.2.0\0";
    VERSION.as_ptr() as *const c_char
}

#[no_mangle]
pub extern "C" fn mong_nhiem_kernel_new() -> *mut MongNhiemKernel {
    let kernel = Box::new(MongNhiemKernel::new());
    Box::into_raw(kernel)
}

#[no_mangle]
pub unsafe extern "C" fn mong_nhiem_kernel_free(kernel: *mut MongNhiemKernel) {
    if !kernel.is_null() {
        drop(Box::from_raw(kernel));
    }
}

#[no_mangle]
pub unsafe extern "C" fn mong_nhiem_register_variable(
    kernel: *mut MongNhiemKernel,
    name: *const c_char,
    initial_value: c_double,
    min_val: c_double,
    max_val: c_double,
    rate_per_sec: c_double,
    is_decay: c_int,
) -> c_int {
    if kernel.is_null() || name.is_null() {
        return -1;
    }
    let k = &mut *kernel;
    if let Ok(name_str) = CStr::from_ptr(name).to_str() {
        k.state_engine.register_variable(
            name_str,
            initial_value,
            min_val,
            max_val,
            rate_per_sec,
            is_decay != 0,
        );
        0
    } else {
        -1
    }
}

#[no_mangle]
pub unsafe extern "C" fn mong_nhiem_register_invariant(
    kernel: *mut MongNhiemKernel,
    variable_name: *const c_char,
    threshold: c_double,
    comparison: *const c_char,
    trigger_action: *const c_char,
) -> c_int {
    if kernel.is_null() || variable_name.is_null() || comparison.is_null() || trigger_action.is_null() {
        return -1;
    }
    let k = &mut *kernel;
    let var_res = CStr::from_ptr(variable_name).to_str();
    let comp_res = CStr::from_ptr(comparison).to_str();
    let act_res = CStr::from_ptr(trigger_action).to_str();

    match (var_res, comp_res, act_res) {
        (Ok(var), Ok(comp), Ok(act)) => {
            k.state_engine.register_trigger(var, threshold, comp, act);
            0
        }
        _ => -1,
    }
}

#[no_mangle]
pub unsafe extern "C" fn mong_nhiem_get_variable(
    kernel: *const MongNhiemKernel,
    name: *const c_char,
    out_value: *mut c_double,
) -> c_int {
    if kernel.is_null() || name.is_null() || out_value.is_null() {
        return -1;
    }
    let k = &*kernel;
    if let Ok(name_str) = CStr::from_ptr(name).to_str() {
        if let Some(val) = k.state_engine.get_variable(name_str) {
            *out_value = val;
            0
        } else {
            -2
        }
    } else {
        -1
    }
}

#[no_mangle]
pub unsafe extern "C" fn mong_nhiem_set_variable(
    kernel: *mut MongNhiemKernel,
    name: *const c_char,
    value: c_double,
) -> c_int {
    if kernel.is_null() || name.is_null() {
        return -1;
    }
    let k = &mut *kernel;
    if let Ok(name_str) = CStr::from_ptr(name).to_str() {
        if k.state_engine.set_variable(name_str, value) {
            0
        } else {
            -2
        }
    } else {
        -1
    }
}

#[no_mangle]
pub unsafe extern "C" fn mong_nhiem_tick(
    kernel: *mut MongNhiemKernel,
    stimulus: *const c_char,
    delta_time: c_double,
    out_result: *mut FfiStepResult,
) -> c_int {
    if kernel.is_null() || out_result.is_null() {
        return -1;
    }
    let k = &mut *kernel;
    let stim_str = if stimulus.is_null() {
        ""
    } else {
        CStr::from_ptr(stimulus).to_str().unwrap_or("")
    };

    let step = k.tick(stim_str, delta_time);

    let verb_c = CString::new(step.action_verb).unwrap_or_default();
    let class_c = CString::new(step.comm_class).unwrap_or_default();
    let msg_c = CString::new(step.comm_message).unwrap_or_default();
    let json_c = CString::new(serde_json::to_string(&step.state_snapshot).unwrap_or_default()).unwrap_or_default();

    let res = &mut *out_result;
    res.action_verb = verb_c.into_raw();
    res.comm_class = class_c.into_raw();
    res.comm_message = msg_c.into_raw();
    res.tick = step.tick;
    res.delta_time = step.delta_time;
    res.state_json = json_c.into_raw();
    res.has_fired_invariants = if step.fired_invariants.is_empty() { 0 } else { 1 };

    0
}

#[no_mangle]
pub unsafe extern "C" fn mong_nhiem_free_step_result(result: *mut FfiStepResult) {
    if result.is_null() {
        return;
    }
    let res = &mut *result;
    if !res.action_verb.is_null() {
        drop(CString::from_raw(res.action_verb));
        res.action_verb = std::ptr::null_mut();
    }
    if !res.comm_class.is_null() {
        drop(CString::from_raw(res.comm_class));
        res.comm_class = std::ptr::null_mut();
    }
    if !res.comm_message.is_null() {
        drop(CString::from_raw(res.comm_message));
        res.comm_message = std::ptr::null_mut();
    }
    if !res.state_json.is_null() {
        drop(CString::from_raw(res.state_json));
        res.state_json = std::ptr::null_mut();
    }
}

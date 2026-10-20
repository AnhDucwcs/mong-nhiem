/**
 * Mộng Nhiễm Cognitive Architecture - C-ABI Native Bindings
 * 
 * Suitable for C, C++, C# (Unity), and GDScript (Godot 4 GDExtension).
 */

#ifndef MONG_NHIEM_H
#define MONG_NHIEM_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct MongNhiemKernel MongNhiemKernel;

typedef struct FfiStepResult {
    char* action_verb;
    char* comm_class;
    char* comm_message;
    uint64_t tick;
    double delta_time;
    char* state_json;
    int has_fired_invariants;
} FfiStepResult;

const char* mong_nhiem_version(void);

MongNhiemKernel* mong_nhiem_kernel_new(void);
void mong_nhiem_kernel_free(MongNhiemKernel* kernel);

int mong_nhiem_register_variable(
    MongNhiemKernel* kernel,
    const char* name,
    double initial_value,
    double min_val,
    double max_val,
    double rate_per_sec,
    int is_decay
);

int mong_nhiem_register_invariant(
    MongNhiemKernel* kernel,
    const char* variable_name,
    double threshold,
    const char* comparison,
    const char* trigger_action
);

int mong_nhiem_get_variable(
    const MongNhiemKernel* kernel,
    const char* name,
    double* out_value
);

int mong_nhiem_set_variable(
    MongNhiemKernel* kernel,
    const char* name,
    double value
);

int mong_nhiem_tick(
    MongNhiemKernel* kernel,
    const char* stimulus,
    double delta_time,
    FfiStepResult* out_result
);

void mong_nhiem_free_step_result(FfiStepResult* result);

#ifdef __cplusplus
}
#endif

#endif /* MONG_NHIEM_H */

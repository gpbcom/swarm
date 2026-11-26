//! The generated structs file must match what the code generator would write today.

use swarm_models_codegen::{default_output_path, default_schema_path, is_stale};

#[test]
fn the_generated_structs_are_current() {
    let stale = is_stale(&default_schema_path(), &default_output_path()).expect("the staleness check should run");
    assert!(
        !stale,
        "src/generated.rs is out of date. Run cargo run -p swarm-models-codegen to regenerate it."
    );
}

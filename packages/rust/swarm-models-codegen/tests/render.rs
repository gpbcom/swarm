//! Integration tests of the schema to Rust renderer.

use std::fs;
use std::path::PathBuf;

use swarm_models_codegen::{default_output_path, default_schema_path, is_stale, render, write, HEADER};

fn fixture_path() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/sample.schema.json")
}

fn fixture() -> String {
    fs::read_to_string(fixture_path()).expect("the fixture is readable")
}

#[test]
fn rendering_the_fixture_succeeds() {
    assert!(render(&fixture()).is_ok());
}

#[test]
fn the_first_line_is_the_header() {
    let output = render(&fixture()).expect("render succeeds");
    assert_eq!(output.lines().next(), Some(HEADER));
}

#[test]
fn every_definition_becomes_a_type() {
    let output = render(&fixture()).expect("render succeeds");
    assert!(output.contains("pub struct Sample"));
    assert!(output.contains("pub enum SampleState"));
}

#[test]
fn two_renders_are_equal() {
    let first = render(&fixture()).expect("render succeeds");
    let second = render(&fixture()).expect("render succeeds");
    assert_eq!(first, second);
}

#[test]
fn rendering_text_that_is_not_json_fails() {
    assert!(render("not json").is_err());
}

#[test]
fn a_missing_output_is_stale() {
    let dir = tempfile::tempdir().expect("temporary directory");
    let output = dir.path().join("generated.rs");
    assert!(is_stale(&fixture_path(), &output).expect("staleness is known"));
}

#[test]
fn a_written_output_is_fresh_and_equals_the_render() {
    let dir = tempfile::tempdir().expect("temporary directory");
    let output = dir.path().join("generated.rs");
    write(&fixture_path(), &output).expect("write succeeds");
    assert!(!is_stale(&fixture_path(), &output).expect("staleness is known"));
    let written = fs::read_to_string(&output).expect("output is readable");
    assert_eq!(written, render(&fixture()).expect("render succeeds"));
}

#[test]
fn an_edited_output_is_stale_again() {
    let dir = tempfile::tempdir().expect("temporary directory");
    let output = dir.path().join("generated.rs");
    write(&fixture_path(), &output).expect("write succeeds");
    let mut text = fs::read_to_string(&output).expect("output is readable");
    text.push_str("// edited by hand\n");
    fs::write(&output, text).expect("output is writable");
    assert!(is_stale(&fixture_path(), &output).expect("staleness is known"));
}

#[test]
fn a_missing_schema_is_an_error() {
    let dir = tempfile::tempdir().expect("temporary directory");
    let schema = dir.path().join("missing.schema.json");
    let output = dir.path().join("generated.rs");
    assert!(is_stale(&schema, &output).is_err());
}

#[test]
fn the_default_paths_point_into_the_models_crate() {
    assert!(default_output_path().ends_with("swarm-models/src/generated.rs"));
    assert!(default_schema_path().ends_with("swarm-models/schemas/swarm_models.schema.json"));
}

//! Entry point of the Swarm desktop shell.

// Release builds on Windows must not open a console window.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    swarm_desktop_lib::run();
}

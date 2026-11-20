//! The Swarm desktop shell: native windows around Ground control and Mission studio.
//!
//! The windows and their pages are declared in `tauri.conf.json`. Nothing else runs here yet.

/// Build the Tauri application from its generated context and run it until its last window closes.
///
/// # Panics
///
/// Panics when the Tauri runtime cannot start, for instance when no display is available.
pub fn run() {
    tauri::Builder::default()
        .run(tauri::generate_context!())
        .expect("the Swarm desktop shell failed to start");
}

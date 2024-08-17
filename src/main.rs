use axum::{extract::State, http::StatusCode, response::IntoResponse, routing::post, Json, Router};
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::{net::SocketAddr, sync::Arc};
use tokio::io::AsyncWriteExt;
use tokio::process::{ChildStdin, Command};
use tokio::sync::Mutex;
static PORT: u16 = 8000;

#[derive(Serialize)]
struct AssistResponse {
    speak: String,
    keep_listening: bool,
    context: Option<String>,
}

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
}

#[derive(Deserialize)]
struct CommandRequest {
    commands: Vec<String>,
}

struct AppState {
    light_process: ChildStdin,
}

impl AppState {
    fn new() -> Self {
        let mut child = Command::new("python")
            .arg("light.py")
            .stdin(std::process::Stdio::piped())
            .spawn()
            .expect("Failed to spawn process");

        let stdin = child.stdin.take().expect("Failed to open stdin");

        AppState {
            light_process: stdin,
        }
    }
}

#[tokio::main]
async fn main() {
    // Create shared state
    let state = Arc::new(Mutex::new(AppState::new()));

    // Define the application routes
    let app = Router::new()
        .route("/assist", post(handle_assist))
        .with_state(state);

    let listener = tokio::net::TcpListener::bind(SocketAddr::from(([0, 0, 0, 0], PORT)))
        .await
        .unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn handle_assist(
    State(state): State<Arc<Mutex<AppState>>>,
    Json(cmd_request): Json<CommandRequest>,
) -> impl IntoResponse {
    let mut to_say = String::new();
    let re = Regex::new(r"\d+").unwrap();

    for command in cmd_request.commands {
        let command = command.to_lowercase();
        if !command.starts_with("jarvis") {
            continue;
        }

        let mut state = state.lock().await;

        if command.contains("light") && command.contains("turn") && command.contains("on") {
            state.light_process.write_all(b"on\n").await.unwrap();
            state.light_process.flush().await.unwrap();
            let response = AssistResponse {
                speak: "Turning on light".to_string(),
                keep_listening: false,
                context: None,
            };
            return (StatusCode::OK, Json(response));
        } else if command.contains("light") && command.contains("turn") && command.contains("off") {
            state.light_process.write_all(b"off\n").await.unwrap();
            state.light_process.flush().await.unwrap();
            let response = AssistResponse {
                speak: "Turning off light".to_string(),
                keep_listening: false,
                context: None,
            };
            return (StatusCode::OK, Json(response));
        } else if command.contains("light") && command.contains("brightness") {
            let numbers: Vec<&str> = re.find_iter(&command).map(|mat| mat.as_str()).collect();
            if !numbers.is_empty() {
                let brightness = numbers[0];
                let cmd = format!("brightness {}\n", brightness);
                state.light_process.write_all(cmd.as_bytes()).await.unwrap();
                state.light_process.flush().await.unwrap();
                let response = AssistResponse {
                    speak: format!("Setting brightness to {} percent", brightness),
                    keep_listening: false,
                    context: None,
                };
                return (StatusCode::OK, Json(response));
            }
        } else {
            if to_say.is_empty() {
                to_say = format!(
                    "Jarvis doesn't know how to {}",
                    command.replace("jarvis ", "")
                );
            }
        }
    }

    let response = AssistResponse {
        speak: to_say,
        keep_listening: false,
        context: None,
    };
    (StatusCode::OK, Json(response))
}

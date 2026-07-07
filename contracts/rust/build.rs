use std::path::PathBuf;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let manifest_dir = PathBuf::from(std::env::var("CARGO_MANIFEST_DIR")?);
    let proto_root = manifest_dir.join("../proto");
    let proto_files = [
        proto_root.join("fluent_dialogue_dora/v1/audio.proto"),
        proto_root.join("fluent_dialogue_dora/v1/vad.proto"),
        proto_root.join("fluent_dialogue_dora/v1/asr.proto"),
        proto_root.join("fluent_dialogue_dora/v1/dialogue.proto"),
        proto_root.join("fluent_dialogue_dora/v1/tts.proto"),
        proto_root.join("fluent_dialogue_dora/v1/session.proto"),
        proto_root.join("fluent_dialogue_dora/v1/playback.proto"),
        proto_root.join("fluent_dialogue_dora/v1/barge_in.proto"),
        proto_root.join("fluent_dialogue_dora/v1/diagnostics.proto"),
    ];
    let protoc = protoc_bin_vendored::protoc_bin_path()?;
    std::env::set_var("PROTOC", protoc);

    let mut config = prost_build::Config::new();
    config.compile_protos(&proto_files, &[proto_root])?;
    Ok(())
}

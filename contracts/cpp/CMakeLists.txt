cmake_minimum_required(VERSION 3.22)
project(fluent_audio_contracts LANGUAGES CXX)

find_package(Protobuf REQUIRED)

file(GLOB_RECURSE FLUENT_AUDIO_CONTRACT_SOURCES CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/generated/*.pb.cc"
)

add_library(fluent_audio_contracts STATIC ${FLUENT_AUDIO_CONTRACT_SOURCES})
target_include_directories(fluent_audio_contracts
    PUBLIC
        "${CMAKE_CURRENT_SOURCE_DIR}/generated"
)
target_link_libraries(fluent_audio_contracts PUBLIC protobuf::libprotobuf)
target_compile_features(fluent_audio_contracts PUBLIC cxx_std_17)

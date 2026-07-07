cmake_minimum_required(VERSION 3.22)
project(fluent_dialogue_dora_contracts LANGUAGES CXX)

find_package(Protobuf REQUIRED)

file(GLOB_RECURSE FLUENT_DIALOGUE_DORA_CONTRACT_SOURCES CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/generated/*.pb.cc"
)

add_library(fluent_dialogue_dora_contracts STATIC ${FLUENT_DIALOGUE_DORA_CONTRACT_SOURCES})
target_include_directories(fluent_dialogue_dora_contracts
    PUBLIC
        "${CMAKE_CURRENT_SOURCE_DIR}/generated"
)
target_link_libraries(fluent_dialogue_dora_contracts PUBLIC protobuf::libprotobuf)
target_compile_features(fluent_dialogue_dora_contracts PUBLIC cxx_std_17)

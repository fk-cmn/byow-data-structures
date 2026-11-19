cmake_minimum_required(VERSION 3.24)
project(byow_cpp LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(byow_core INTERFACE)
target_include_directories(byow_core INTERFACE "${CMAKE_CURRENT_SOURCE_DIR}/src")
target_compile_options(byow_core INTERFACE "$<$<CXX_COMPILER_ID:MSVC>:/utf-8>")
add_executable(relic_engine src/main.cpp)
target_link_libraries(relic_engine PRIVATE byow_core)
add_executable(core_tests tests/core_tests.cpp)
target_link_libraries(core_tests PRIVATE byow_core)
add_executable(session_tests tests/session_tests.cpp)
target_link_libraries(session_tests PRIVATE byow_core)
enable_testing()
add_test(NAME core_tests COMMAND core_tests)
add_test(NAME session_tests COMMAND session_tests)

option(BYOW_BUILD_NATIVE "Build the SFML desktop prototype" ON)
if(BYOW_BUILD_NATIVE)
    include(FetchContent)
    set(BUILD_SHARED_LIBS ON CACHE BOOL "Build SFML shared libraries" FORCE)
    set(SFML_BUILD_AUDIO OFF CACHE BOOL "" FORCE)
    set(SFML_BUILD_NETWORK OFF CACHE BOOL "" FORCE)
    set(SFML_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
    set(SFML_BUILD_TEST_SUITE OFF CACHE BOOL "" FORCE)
    FetchContent_Declare(SFML
        GIT_REPOSITORY https://github.com/SFML/SFML.git
        GIT_TAG 0fa201c969e48ecc253581c5841ce73f44d42f49) # SFML 3.0.2
    FetchContent_MakeAvailable(SFML)
    add_executable(byow_native src/native/main.cpp src/native/music.cpp)
    target_include_directories(byow_native SYSTEM PRIVATE "${sfml_SOURCE_DIR}/extlibs/headers/miniaudio")
    target_link_libraries(byow_native PRIVATE byow_core SFML::Graphics)
    if(UNIX)
        find_package(Threads REQUIRED)
        target_link_libraries(byow_native PRIVATE Threads::Threads ${CMAKE_DL_LIBS})
    endif()
    # Use executable-relative assets in a release; source assets in a developer build.
    target_compile_definitions(byow_native PRIVATE BYOW_SOURCE_ASSETS="${CMAKE_CURRENT_SOURCE_DIR}/assets")
    if(WIN32)
        foreach(runtime_dll libgcc_s_seh-1.dll libstdc++-6.dll libwinpthread-1.dll)
            execute_process(COMMAND "${CMAKE_CXX_COMPILER}" "-print-file-name=${runtime_dll}"
                OUTPUT_VARIABLE runtime_path OUTPUT_STRIP_TRAILING_WHITESPACE)
            if(EXISTS "${runtime_path}")
                add_custom_command(TARGET byow_native POST_BUILD
                    COMMAND ${CMAKE_COMMAND} -E copy_if_different "${runtime_path}" $<TARGET_FILE_DIR:byow_native>)
            endif()
        endforeach()
        add_custom_command(TARGET byow_native POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_RUNTIME_DLLS:byow_native> $<TARGET_FILE_DIR:byow_native>
            COMMAND_EXPAND_LISTS)
    endif()
    install(TARGETS byow_native RUNTIME DESTINATION .)
    install(DIRECTORY assets/ DESTINATION assets)
    install(FILES "${sfml_SOURCE_DIR}/license.md" DESTINATION licenses RENAME SFML.md)
    install(FILES licenses/TUFFY.md DESTINATION licenses)
    install(FILES licenses/NotoSansSC-OFL.txt DESTINATION licenses)
    install(FILES licenses/LXGWWenKaiLite-OFL.txt DESTINATION licenses)
    install(FILES licenses/LongCang-OFL.txt licenses/UnifrakturMaguntia-OFL.txt DESTINATION licenses)
    if(WIN32)
        foreach(runtime_dll libgcc_s_seh-1.dll libstdc++-6.dll libwinpthread-1.dll)
            execute_process(COMMAND "${CMAKE_CXX_COMPILER}" "-print-file-name=${runtime_dll}"
                OUTPUT_VARIABLE runtime_path OUTPUT_STRIP_TRAILING_WHITESPACE)
            if(EXISTS "${runtime_path}")
                install(FILES "${runtime_path}" DESTINATION .)
            endif()
        endforeach()
        install(FILES
            $<TARGET_FILE:sfml-graphics>
            $<TARGET_FILE:sfml-window>
            $<TARGET_FILE:sfml-system>
            DESTINATION .)
    endif()
    install(FILES README.md DESTINATION .)
endif()

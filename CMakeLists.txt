cmake_minimum_required(VERSION 3.20)
project(watermelon-oss)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED YES)

file(GLOB_RECURSE SOURCES "src/*.cc")

add_executable("wpp-oss" ${SOURCES})

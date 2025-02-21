cmake_minimum_required(VERSION 3.20)
project(watermelon-oss)

file(GLOB_RECURSE SOURCES "src/*.cpp")

add_executable("wpp-oss" ${SOURCES})

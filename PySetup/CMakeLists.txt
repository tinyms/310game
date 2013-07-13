project(PySetup)
cmake_minimum_required(VERSION 2.8)
aux_source_directory(. SRC_LIST)
SET(CMAKE_BUILD_TYPE "Release")

include_directories("d:/Python33/include/")
LINK_DIRECTORIES("d:/Python33/libs/")
LINK_LIBRARIES("python33.lib")

add_executable(${PROJECT_NAME} ${SRC_LIST} PySetup.rc)

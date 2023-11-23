cmake_minimum_required(VERSION 3.17)
project(semestral_work)

set(CMAKE_CXX_STANDARD 14)
add_compile_options(-O3 -Wall -Wextra -pedantic)

############ OpenMP ############
# macOS: brew install libomp
find_package(OpenMP REQUIRED)
set(OMP_LIBRARIES "OpenMP::OpenMP_CXX")

############ MPI ############
# macOS: brew install openmpi
find_package(MPI REQUIRED)
include_directories(${MPI_INCLUDE_PATH})

############ MPI ############
add_executable(semestral_work main.cpp InputReader.cpp InputReader.h Typing.h Chessboard.cpp Chessboard.h ChessPiece.h Logger.cpp Logger.h ProblemInstance.cpp ProblemInstance.h Solver.cpp Solver.h Clock.cpp Clock.h Solution.cpp Solution.h Cli.cpp Cli.h messages.h)

target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE ${OMP_LIBRARIES} ${MPI_LIBRARIES})

if(MPI_COMPILE_FLAGS)
    set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES
            COMPILE_FLAGS "${MPI_COMPILE_FLAGS} ${OpenMP_CXX_FLAGS}")
endif()

if(MPI_LINK_FLAGS)
    set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES
            LINK_FLAGS "${MPI_LINK_FLAGS} ${OpenMP_CXX_FLAGS}")
endif()

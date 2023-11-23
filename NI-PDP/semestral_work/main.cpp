#include <iostream>
#include "InputReader.h"
#include "Solver.h"
#include "Cli.h"


int main(int argc, const char *argv[]) {
    // Start MPI scope
    MPI_Init(nullptr, nullptr);

    // std::string defaultPath = "../input";
    std::string inputPath;
    auto problems = InputReader::readFromPath(Cli::parseInput(argc, argv));


    int my_rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);

    int problemCnt = 1;
    for (auto &problem: problems) {
        auto problemSolver = Solver(problem);
        problemSolver.solve();

        // delegate solution displaying to MASTER SLAVE
        if (my_rank == 0) {
            std::cout << problemCnt << ")_________________________________________________________________" << std::endl;
            // print solution
            problem->outputSolution();
            std::cout << "________________________________________________________________" << std::endl;
        }
        problemCnt++;
    }

    // End MPI scope
    MPI_Finalize();
    for (auto &problem : problems) {
        delete problem;
    }

    return 0;
}

//
// Created by Mykyta on 28/02/2021.
//

#pragma once

#include <list>
#include <deque>
#include <omp.h>
#include <mpi.h>
#include "ProblemInstance.h"
#include "Clock.h"

class Solver {
private:
    ProblemInstance *problemToSolve;
    // base attributes for solution monitoring
    int16_t bestSolutionDepth;
    // a.k.a maxDepth + 1 at initialization
    int16_t curUpperBoundDepth;

    Clock clock;
    int recCallsCnt;

    std::deque<Chessboard> expandBFS(Chessboard board, size_t cntStatesToExpand, bool considerFirstLvl = true);
    void solveDFSChessboard(Chessboard board);
    bool isFoundBestPossibleSolution() const;

    void tryToUpdateSolution(Chessboard &board, bool criticalSection = false);

    // MPI scope
    MpiSlaveSolutionMessage createSlaveSolutionMessage() const;
    void deserializeSlaveMessageAndTryToUpdateMaster(MpiSlaveSolutionMessage &message);
public:
    explicit Solver(ProblemInstance *problem);
    void solve();

    // lets keep current best current moving history
    std::vector<Coord_t> curBestSolutionMovingHistory;
};



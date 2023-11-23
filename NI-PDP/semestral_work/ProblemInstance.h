//
// Created by Mykyta on 28/02/2021.
//

#pragma once

#include <iostream>

#include "Chessboard.h"
#include "Solution.h"

class ProblemInstance {
private:
    Chessboard *chessboard;
    // 2*k^2, upper fence
    int16_t maxDepth;
    int16_t minDepthForBestSolution;

    Solution *solution;
public:
    ProblemInstance(int16_t maxDepth, int16_t minDepth, Chessboard *chessboard);
    Chessboard* getChessboard();

    int16_t getMaxDepth() const;
    int16_t getMinDepthForBestSolution() const;

    void setSolution(Solution *solution);
    void outputSolution() const;


    // help functions scope
    friend std::ostream& operator<<(std::ostream& os, const ProblemInstance* obj);
    friend std::ostream& operator<<(std::ostream& os, const ProblemInstance& obj);
};

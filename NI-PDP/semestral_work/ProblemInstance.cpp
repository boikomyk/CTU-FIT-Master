//
// Created by Mykyta on 28/02/2021.
//

#include <set>
#include "ProblemInstance.h"

ProblemInstance::ProblemInstance(int16_t maxDepth, int16_t minDepth, Chessboard *chessboard):
chessboard(chessboard), maxDepth(maxDepth), minDepthForBestSolution(minDepth) {
    this->solution = nullptr;
}

void ProblemInstance::setSolution(Solution *solution) {
    this->solution = solution;
}

Chessboard *ProblemInstance::getChessboard() {
    return this->chessboard;
}

int16_t ProblemInstance::getMaxDepth() const {
    return this->maxDepth;
}

int16_t ProblemInstance::getMinDepthForBestSolution() const {
    return this->minDepthForBestSolution;
}

std::ostream &operator<<(std::ostream &os, const ProblemInstance *obj) {
    os << *obj;
    return os;
}

std::ostream &operator<<(std::ostream &os, const ProblemInstance &obj) {
    os << "- maxDepth: " << std::to_string(obj.maxDepth) << "\n";
    os << "- minDepthForBestSolution: " << std::to_string(obj.minDepthForBestSolution) << "\n";
    os << obj.chessboard;
    return os;
}

void ProblemInstance::outputSolution() const {
    if (this->solution == nullptr) {
        std::cout << "Not solved yet" << std::endl;
    } else {
        std::cout << "Time [ms]: " << std::to_string(this->solution->time) << std::endl;
        std::cout << "Price: " << std::to_string(this->solution->price) << std::endl;
        std::cout << "Calls number: " << std::to_string(this->solution->callsNumber) << std::endl;
        std::cout << "Moving history: ";
        auto movingHistory = solution->movingHistory;

        std::set<Coord_t> enemiesPositions;
        for(auto &moveInHistory: movingHistory) {
            std::cout << "[" << std::to_string(moveInHistory.first) << "," << std::to_string(moveInHistory.second) << "]";
            if (this->chessboard->get(moveInHistory) == EnemyPiece && enemiesPositions.find(moveInHistory) == enemiesPositions.end()) {
                enemiesPositions.insert(moveInHistory);
                std::cout << "*";
            }
            if (&moveInHistory != &movingHistory.back()) std::cout << ", ";
        }
        std::cout << std::endl;
    }
}

//
// Created by Mykyta on 13.04.2021.
//

#pragma once

// ____________________________ MPI MESSAGING SCOPE ______________________________\/
#define BOARD_SIDE_MAX_LENGTH 19
#define BOARD_MAX_SIZE (BOARD_SIDE_MAX_LENGTH*BOARD_SIDE_MAX_LENGTH)
#define UPPER_BOUND_STEPS_CNT (2 * BOARD_SIDE_MAX_LENGTH * BOARD_SIDE_MAX_LENGTH)


struct MpiBoardMessage {
    int8_t size;
    int8_t knightCoord[2];
    int8_t bishopCoord[2];
    bool boardEnemiesCoords[BOARD_MAX_SIZE];
    int16_t actualEnemiesCnt;
    ChessPiece whoOnTurn;
    int8_t posToMove[2];
    int16_t movingHistorySize;
    // moving history for X, Y coordinates
    int8_t movingHistory_X[UPPER_BOUND_STEPS_CNT];
    int8_t movingHistory_Y[UPPER_BOUND_STEPS_CNT];
    int16_t currentUpperBound = UPPER_BOUND_STEPS_CNT;
    bool keepRunningSlave = true;
};

struct MpiSlaveSolutionMessage {
    // price aka movingHistorySize
    int16_t price;
    int16_t movingHistorySize;
    // moving history for X, Y coordinates
    int8_t movingHistory_X[UPPER_BOUND_STEPS_CNT];
    int8_t movingHistory_Y[UPPER_BOUND_STEPS_CNT];
    int recCallsCnt = 0;
};
// ____________________________ MPI MESSAGING SCOPE ______________________________/\
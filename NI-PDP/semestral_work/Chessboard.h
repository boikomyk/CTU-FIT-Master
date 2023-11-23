//
// Created by Mykyta on 27/02/2021.
//

#pragma once


#include <vector>
#include <ostream>
#include <iostream>

#include <map>
#include <list>
#include <algorithm>

#include "Typing.h"
#include "ChessPiece.h"
#include "messages.h"


class Chessboard {
private:
    static const std::vector<Coord_t> BISHOP_MOVEMENT_DIRECTIONS;
    static const std::vector<Coord_t> KNIGHT_MOVEMENT_DIRECTIONS;

    // 20>size>5; max_size = 19
    int8_t size;
    Coord_t knightCoord;
    Coord_t bishopCoord;
    std::vector<bool> boardEnemiesCoords;
    int16_t actualEnemiesCnt;
    ChessPiece whoOnTurn;
    Coord_t posToMove;

    std::vector<Coord_t> movingHistory;

    int8_t getBoardSize() const;
    void unsetEnemyPiece(Coord_t &coord);

    // algorithm funcs:
    std::vector<Coord_t> next() const;
    int8_t val(Coord_t &coord) const;

    std::vector<Coord_t> nextBishopPositions() const;
    std::vector<Coord_t> nextKnightPositions() const;
    bool isLeadToDiagonalWithAnyEnemy(Coord_t &coord) const;

    // help functions scope
    int16_t getFlattenIndex(Coord_t &coord) const;
    bool isBoard(Coord_t &coord) const;
public:
    explicit Chessboard(int8_t size);
    void setEnemyPiece(Coord_t &coord);
    void setKnight(Coord_t &coord);
    void setBishop(Coord_t &coord);
    void setActualEnemiesCnt(int16_t enemiesCnt);
    ChessPiece get(Coord_t &coord) const;
    int16_t getActualEnemiesCnt() const;
    int16_t getFastForwardEnemiesCntForPos(Coord_t &coord) const;
    void moveActiveChessPieceToNextPos();
    void setNextPosToMove(Coord_t coord);

    int16_t getMovingHistorySize() const;
    std::vector<Coord_t> getMovingHistory() const;

    // algorithm funcs:
    std::vector<Coord_t> getNextOrderedByVal() const;

    // help functions scope
    friend std::ostream& operator<<(std::ostream& os, const Chessboard* obj);
    friend std::ostream& operator<<(std::ostream& os, const Chessboard& obj);

    // MPI serializing functions
    MpiBoardMessage serialize() const;
    static Chessboard deserialize(MpiBoardMessage &message);
};

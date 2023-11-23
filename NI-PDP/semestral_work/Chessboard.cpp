//
// Created by Mykyta on 27/02/2021.
//

#include "Chessboard.h"

const std::vector<Coord_t> Chessboard::BISHOP_MOVEMENT_DIRECTIONS =
        std::vector<Coord_t>({
                                     Coord_t(-1, -1),
                                     Coord_t(-1, 1),
                                     Coord_t(1, -1),
                                     Coord_t(1, 1)
                             });

const std::vector<Coord_t> Chessboard::KNIGHT_MOVEMENT_DIRECTIONS =
        std::vector<Coord_t>({
                                     Coord_t(-2, -1),
                                     Coord_t(-1, -2),
                                     Coord_t(1, 2),
                                     Coord_t(1, -2),
                                     Coord_t(2, -1),
                                     Coord_t(2, 1),
                                     Coord_t(-1, 2),
                                     Coord_t(-2, 1)
                             });
/**
 * Return an index of the chessboard collapsed into one dimension.
 * @param coord
 * @return
 */
int16_t Chessboard::getFlattenIndex(Coord_t &coord) const {
    return static_cast<int16_t>(this->size) * coord.second + coord.first;
}

Chessboard::Chessboard(int8_t size) {
    this->size = size;
    this->actualEnemiesCnt = 0;
    this->boardEnemiesCoords.resize(static_cast<int16_t>(this->size) * size, false);

    // first on turn is Bishop
    this->whoOnTurn = ChessPiece::Bishop;
}

ChessPiece Chessboard::get(Coord_t &coord) const {
    if (this->boardEnemiesCoords[this->getFlattenIndex(coord)]) {
        return EnemyPiece;
    } else if (this->knightCoord == coord) {
        return Knight;
    } else if (this->bishopCoord == coord) {
        return Bishop;
    }
    return EmptyCell;
}

void Chessboard::setEnemyPiece(Coord_t &coord) {
    this->boardEnemiesCoords[this->getFlattenIndex(coord)] = true;
}

void Chessboard::unsetEnemyPiece(Coord_t &coord) {
    int16_t flattenIndex = this->getFlattenIndex(coord);
    if (this->boardEnemiesCoords[flattenIndex]) {
        this->boardEnemiesCoords[this->getFlattenIndex(coord)] = false;
        this->actualEnemiesCnt -= 1;
    }
}

void Chessboard::setKnight(Coord_t &coord) {
    this->knightCoord = coord;
}

void Chessboard::setBishop(Coord_t &coord) {
    this->bishopCoord = coord;
}

int8_t Chessboard::getBoardSize() const {
    return this->size;
}

void Chessboard::setActualEnemiesCnt(int16_t enemiesCnt) {
    this->actualEnemiesCnt = enemiesCnt;
}

int16_t Chessboard::getActualEnemiesCnt() const {
    return this->actualEnemiesCnt;
}

int16_t Chessboard::getFastForwardEnemiesCntForPos(Coord_t &coord) const {
    if (this->get(coord) == EnemyPiece) {
        return this->actualEnemiesCnt - 1;
    }
    return this->actualEnemiesCnt;
}

bool Chessboard::isBoard(Coord_t &coord) const {
    return coord.first >=0 && coord.first < size && coord.second >= 0 && coord.second < size;
}

std::vector<Coord_t> Chessboard::nextBishopPositions() const {
    std::vector<Coord_t> positionsToGo;

    for(auto &direction: Chessboard::BISHOP_MOVEMENT_DIRECTIONS) {
        for(int8_t inc = 1; inc < size; inc++) {
            // create next possible coord position
            Coord_t possibleNextPos = Coord_t(
                    bishopCoord.first + (inc * direction.first),
                    bishopCoord.second + (inc * direction.second)
            );

            // if the coord doesn't belong to the board
            if (!isBoard(possibleNextPos)) {
                break;
            }

            auto chessPieceOnNextPos = get(possibleNextPos);
            if (chessPieceOnNextPos == Knight) {
                break;
            } else if (chessPieceOnNextPos == EnemyPiece) {
                positionsToGo.push_back(possibleNextPos);
                break;
            } else if (chessPieceOnNextPos == EmptyCell) {
                positionsToGo.push_back(possibleNextPos);
            }
        }
    }
    return positionsToGo;
}

std::vector<Coord_t> Chessboard::nextKnightPositions() const {
    std::vector<Coord_t> positionsToGo;

    for(auto &direction: Chessboard::KNIGHT_MOVEMENT_DIRECTIONS) {
        // create next possible coord position
        Coord_t possibleNextPos = Coord_t(
                knightCoord.first + direction.first,
                knightCoord.second + direction.second
        );

        // if the coord doesn't belong to the board
        if (!isBoard(possibleNextPos)) {
            continue;
        }

        auto chessPieceOnNextPos = get(possibleNextPos);
        if (chessPieceOnNextPos == Bishop) {
            continue;
        }
        positionsToGo.push_back(possibleNextPos);
    }
    return positionsToGo;
}

std::vector<Coord_t> Chessboard::next() const {
    switch (this->whoOnTurn) {
        case Bishop:
            return this->nextBishopPositions();
        case Knight:
            return this->nextKnightPositions();
        default:
            throw std::invalid_argument("Unsupported chess piece type.");
    }
}

bool Chessboard::isLeadToDiagonalWithAnyEnemy(Coord_t &coord) const {
    for(auto &direction: Chessboard::BISHOP_MOVEMENT_DIRECTIONS) {
        for(int8_t inc = 1; inc < size; inc++) {
            // create next possible coord position
            Coord_t possibleNextPos = Coord_t(
                    coord.first + (inc * direction.first),
                    coord.second + (inc * direction.second)
            );

            // if the coord doesn't belong to the board
            if (!isBoard(possibleNextPos)) {
                break;
            }

            auto chessPieceOnNextPos = get(possibleNextPos);
            if (chessPieceOnNextPos == Knight) {
                break;
            }
            if (chessPieceOnNextPos == EnemyPiece) {
                return true;
            }
        }
    }
    return false;
}

int8_t Chessboard::val(Coord_t &coord) const {
    auto chessPieceByCoord = get(coord);

    // common for bishop and knight logic scope
    if (chessPieceByCoord == EnemyPiece) {
        return 2;
    }
    // bishop same diagonal logic
    if (whoOnTurn == Bishop && isLeadToDiagonalWithAnyEnemy(coord)) {
        return 1;
    }
    return 0;
}

std::vector<Coord_t> Chessboard::getNextOrderedByVal() const {
    std::vector<Coord_t> nextPositions = this->next();

    std::vector<std::pair<Coord_t, uint8_t>> valuedPositions;
    valuedPositions.reserve(nextPositions.size());
    for (auto &nextPos: nextPositions) {
        valuedPositions.emplace_back(std::make_pair(nextPos, this->val(nextPos)));
    }

    std::stable_sort(valuedPositions.begin(), valuedPositions.end(),
                     [](const std::pair<Coord_t, uint8_t> &lhs, const std::pair<Coord_t, uint8_t> &rhs){
        return lhs.second > rhs.second;
    });

    std::vector<Coord_t> nextPositionsOrderedByVal;
    nextPositionsOrderedByVal.reserve(valuedPositions.size());

    for (auto &valuedPos: valuedPositions) {
        nextPositionsOrderedByVal.push_back(valuedPos.first);
    }
    return nextPositionsOrderedByVal;
}

void Chessboard::setNextPosToMove(Coord_t coord) {
    this->posToMove = coord;
}

void Chessboard::moveActiveChessPieceToNextPos() {
    // unset possible enemy and update moving history
    this->unsetEnemyPiece(this->posToMove);

    // update active chessPiece position and switch active "player"
    switch (this->whoOnTurn) {
        case Bishop:
            this->bishopCoord = this->posToMove;
            this->whoOnTurn = Knight;
            break;
        case Knight:
            this->knightCoord = this->posToMove;
            this->whoOnTurn = Bishop;
            break;
        default:
            throw std::invalid_argument("Unsupported chess piece type.");
    }
    // update current moving history
    this->movingHistory.push_back(this->posToMove);
}

std::vector<Coord_t> Chessboard::getMovingHistory() const {
    return this->movingHistory;
}

int16_t Chessboard::getMovingHistorySize() const {
    return this->movingHistory.size();
}

std::ostream &operator<<(std::ostream &os, const Chessboard *obj) {
    os << *obj;
    return os;
}

std::ostream &operator<<(std::ostream &os, const Chessboard &obj) {
    os  << "- Board of size: " << std::to_string(obj.size) << "\n";
    os  << "- Actual enemy chess pieces count: " << std::to_string(obj.actualEnemiesCnt) << "\n";
    os  << "- Board text representation:\n";
    for(int8_t y = 0; y < obj.size; y++) {
        for(int8_t x = 0; x < obj.size; x++) {
            auto coord = Coord_t (x,y);
            switch (obj.get(coord)) {
                case Knight:
                    os << "J";
                    break;
                case Bishop:
                    os << "S";
                    break;
                case EnemyPiece:
                    os << "P";
                    break;
                case EmptyCell:
                    os << "-";
                    break;
            }
        }
        os << "\n";
    }
    return os;
}

/**
 * Function wrapping current chessboard state to MpiBoardMessage object (message addressed to slave)
 * @return
 */
MpiBoardMessage Chessboard::serialize() const {
    MpiBoardMessage message = MpiBoardMessage();

    message.size = size;

    message.knightCoord[0] = knightCoord.first;
    message.knightCoord[1] = knightCoord.second;

    message.bishopCoord[0] = bishopCoord.first;
    message.bishopCoord[1] = bishopCoord.second;

    for (size_t indx = 0; indx < boardEnemiesCoords.size(); indx++) {
        message.boardEnemiesCoords[indx] = boardEnemiesCoords[indx];
    }

    message.actualEnemiesCnt = actualEnemiesCnt;
    message.whoOnTurn = whoOnTurn;
    message.posToMove[0] = posToMove.first;
    message.posToMove[1] = posToMove.second;
    message.movingHistorySize = movingHistory.size();

    for (size_t indx = 0; indx < movingHistory.size(); indx++) {
        message.movingHistory_X[indx] = movingHistory[indx].first;
        message.movingHistory_Y[indx] = movingHistory[indx].second;
    }
    return message;
}

/**
 * Static function unwrapping board state from MpiBoardMessage object
 * @param message
 * @return
 */
Chessboard Chessboard::deserialize(MpiBoardMessage &message) {
    Chessboard board = Chessboard(message.size);

    board.knightCoord = Coord_t(message.knightCoord[0], message.knightCoord[1]);
    board.bishopCoord = Coord_t(message.bishopCoord[0], message.bishopCoord[1]);

    int boardSize = static_cast<int>(message.size) * message.size;
    for (int indx = 0; indx < boardSize; indx++) {
        board.boardEnemiesCoords[indx] = message.boardEnemiesCoords[indx];
    }

    board.actualEnemiesCnt = message.actualEnemiesCnt;
    board.whoOnTurn = message.whoOnTurn;
    board.posToMove = Coord_t(message.posToMove[0], message.posToMove[1]);


    board.movingHistory.reserve(message.movingHistorySize);
    for (auto indx = 0; indx < message.movingHistorySize; indx++) {
        board.movingHistory.emplace_back(Coord_t(message.movingHistory_X[indx], message.movingHistory_Y[indx]));
    }
    return board;
}

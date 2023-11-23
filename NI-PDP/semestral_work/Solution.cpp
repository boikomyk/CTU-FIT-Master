//
// Created by Mykyta on 02/03/2021.
//

#include "Solution.h"

Solution::Solution(int time, int16_t price, int callsNumber, std::vector<Coord_t> &movingHistory): time(time), price(price), callsNumber(callsNumber) {
    this->movingHistory = movingHistory;
}

//
// Created by Mykyta on 02/03/2021.
//

#pragma once


#include <cstdint>
#include <ostream>
#include <vector>
#include "Typing.h"



class Solution {
public:
    int time;
    int16_t price;
    int callsNumber;
    std::vector<Coord_t> movingHistory;
    Solution(int time, int16_t price, int callsNumber, std::vector<Coord_t> &movingHistory);
};



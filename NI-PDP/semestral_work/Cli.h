//
// Created by Mykyta on 02/03/2021.
//

#pragma once


#include <string>
#include <cstring>
#include <stdexcept>


class Cli {
public:
    static std::string parseInput(int argc, const char *argv[]);
};

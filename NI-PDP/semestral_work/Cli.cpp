//
// Created by Mykyta on 02/03/2021.
//

#include "Cli.h"

/**
 * Returns path passed with '--path'
 * @param argc
 * @param argv
 * @return
 */
std::string Cli::parseInput(int argc, const char *argv[]) {
    if (argc != 3 || std::strcmp(argv[1], "--path") != 0) {
        throw std::invalid_argument("Invalid path to input. Please pass path with '--path' arg.");
    }
    return std::string(argv[2]);
}

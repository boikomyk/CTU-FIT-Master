//
// Created by Mykyta on 27/02/2021.
//

#pragma once

#include <vector>
#include <dirent.h>
#include <fstream>
#include <sstream>
#include <iostream>
#include <string>
#include <cstring>
#include <sys/stat.h>
#include <stdexcept>
#include <algorithm>
#include <cstdio>
#include <cctype>


#include "Logger.h"
#include "Chessboard.h"
#include "ProblemInstance.h"

class InputReader {
public:
    static std::vector<ProblemInstance*> readFromPath(const std::string& path);
private:
    static std::vector<ProblemInstance*> readFromDir(const std::string& dirPath);
    static ProblemInstance* readFromFile(const std::string& filePath);
};



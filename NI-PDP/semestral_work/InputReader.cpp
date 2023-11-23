//
// Created by Mykyta on 27/02/2021.
//

#include "InputReader.h"

/**
 * Custom comparator function for directory filenames sorting purposes
 * @param a
 * @param b
 * @return
 */
bool compare_filenames(const std::string &a, const std::string &b)
{
    std::string digits = "0123456789";
    auto isDigit = [&](std::string &str) { return str.find_first_not_of(digits) == std::string::npos; };

    // check case when filenames are marked with numbers
    size_t first_indexA = a.find_first_of(digits);
    size_t first_indexB = b.find_first_of(digits);
    if (first_indexA != std::string::npos && first_indexB != std::string::npos) {
        std::string possibleNumA = a.substr(first_indexA, a.find_last_of(digits) - first_indexA + 1);
        std::string possibleNumB = b.substr(first_indexB, b.find_last_of(digits) - first_indexB + 1);

        // check if formatted strings respond to number format
        if (isDigit(possibleNumA) && isDigit(possibleNumB)){
            return std::stoi(possibleNumA) < std::stoi(possibleNumB);
        }
    }

    // text type comparison
    char *pA, *pB;
    long A = strtol(a.c_str(), &pA, 10),
            B = strtol(b.c_str(), &pB, 10);
    if (A < B)
        return true;
    if (A == B)
        return strcmp(pA, pB);
    return false;
}

/**
 * Function that reads ProblemInstances from an input path whether directory or file
 * @param path
 * @return
 */
std::vector<ProblemInstance*> InputReader::readFromPath(const std::string& path) {
    struct stat info{};
    int statRC = stat(path.c_str(), &info);

    if(statRC != 0)
    {
        switch (errno) {
            case ENOENT:
                throw std::invalid_argument("Invalid path: something along the path does not exist.");
            case ENOTDIR:
                throw std::invalid_argument("Invalid path: something in path prefix is not a dir.");
            default:
                throw std::invalid_argument("Invalid path.");
        }
    }

    std::vector<ProblemInstance*> problemsInstances;

    // in case of directory input
    if (S_ISDIR(info.st_mode)) {
        problemsInstances = readFromDir(path);
    // in case of file input
    } else if (S_ISREG(info.st_mode)) {
        problemsInstances.push_back(readFromFile(path));
    }

    return problemsInstances;
}

/**
 * Function that reads ProblemInstances from a directory
 * @param dirPath
 * @return
 */
std::vector<ProblemInstance *> InputReader::readFromDir(const std::string &dirPath) {
    std::string formattedDirPath = dirPath;
    if (dirPath.back() != '/') {
        formattedDirPath += "/";
    }

    struct dirent *dir;
    DIR *d = opendir((formattedDirPath).c_str());
    std::vector<std::string> fileNames;

    if (d) {
        Logger::info("Reading from dir: " +  formattedDirPath);
        while ((dir = readdir(d)) != nullptr) {
            if (std::string(dir->d_name).find("txt") != std::string::npos) {
                fileNames.emplace_back(formattedDirPath + dir->d_name);
            }
        }
        closedir(d);
    } else if (ENOENT == errno) {
        throw std::invalid_argument("Directory doesn't exists.");
    } else {
        throw std::invalid_argument("Opendir() failed for some other reason.");
    }

    std::sort(fileNames.begin(), fileNames.end(), compare_filenames);

    std::vector<ProblemInstance*> problemsInstances;
    problemsInstances.reserve(fileNames.size());

    for (auto &fileName: fileNames) {
        problemsInstances.push_back(readFromFile(fileName));
    }
    return problemsInstances;
}

/**
 * Function that reads ProblemInstance from a file
 * @param dirPath
 * @return
 */
ProblemInstance* InputReader::readFromFile(const std::string &filePath) {
    std::ifstream infile(filePath);

    if (!infile.good()) {
        throw std::invalid_argument("Invalid path or file: " + filePath);
    }

    Logger::info("Reading input from file: " +  filePath);

    std::string boardSize;
    getline(infile,boardSize);
    std::string maxDepth;
    getline(infile,maxDepth);
    auto *chessboard = new Chessboard(std::stoi(boardSize));

    Coord_t curCoord = Coord_t (0,0);
    int16_t enemiesCnt = 0;

    std::string line;
    while (std::getline(infile, line)) {
        std::istringstream iss(line);
        char chessPiece;

        while(iss >> chessPiece) {
            switch(chessPiece) {
                case 'P':
                    chessboard->setEnemyPiece(curCoord);
                    enemiesCnt++;
                    break;
                case 'J':
                    chessboard->setKnight(curCoord);
                    break;
                case 'S':
                    chessboard->setBishop(curCoord);
                    break;
                case '-':
                    break;
                default:
                    throw std::invalid_argument("Invalid char from input file: " + filePath);
            }
            // move X coord
            curCoord.first += 1;
        }

        // move Y coord
        curCoord.first = 0;
        curCoord.second += 1;
    }
    chessboard->setActualEnemiesCnt(enemiesCnt);
    return new ProblemInstance(std::stoi(maxDepth), enemiesCnt, chessboard);
}

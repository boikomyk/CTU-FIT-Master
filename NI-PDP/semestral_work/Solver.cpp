//
// Created by Mykyta on 28/02/2021.
//

#include "Solver.h"

Solver::Solver(ProblemInstance *problem) {
    // set problem
    problemToSolve = problem;
    // init default attributes/properties for solver
    bestSolutionDepth = problem->getMinDepthForBestSolution();
    curUpperBoundDepth = problem->getMaxDepth() + 1;
    // recursive funcs calls counter and custom clocker
    recCallsCnt = 0;
    clock = Clock();
}

bool Solver::isFoundBestPossibleSolution() const {
    // best found solution price is equal to lower fence
    return curUpperBoundDepth == bestSolutionDepth;
}

void Solver::tryToUpdateSolution(Chessboard &board, bool criticalSection) {
    // board.getMovingHistorySize = current depth
    // curUpperBoundDepth = curBestSolutionDepth
    if (criticalSection) {
        #pragma omp critical
        {
            if (curUpperBoundDepth > board.getMovingHistorySize()) {
                curUpperBoundDepth = board.getMovingHistorySize();
                curBestSolutionMovingHistory = board.getMovingHistory();
            }
        }
    } else {
        if (curUpperBoundDepth > board.getMovingHistorySize()) {
            curUpperBoundDepth = board.getMovingHistorySize();
            curBestSolutionMovingHistory = board.getMovingHistory();
        }
    }
}

/**
 * Expand BFS function that prepares queue with tasks
 * @param depth
 * @return
 */
std::deque<Chessboard> Solver::expandBFS(Chessboard board, size_t cntStatesToExpand, bool considerFirstLvl) {
    if (!considerFirstLvl) {
        board.moveActiveChessPieceToNextPos();
    }

    std::deque<Chessboard> tasksQueue;

    // expand states using BFS with depth 1
    for (auto nextPriorPosition: board.getNextOrderedByVal()) {
        board.setNextPosToMove(nextPriorPosition);
        tasksQueue.push_back(board);
    }

    // check if the needed count of states was already expanded at depth 1
    // return in case we achieved needed count or continue expansion otherwise
    if (cntStatesToExpand <= tasksQueue.size()) return tasksQueue;

    // expand states while:
    // 1. do not achieved needed count or
    // 2. queue with states are not empty or
    // 3. solution will be found
    while (!tasksQueue.empty() && cntStatesToExpand > tasksQueue.size()) {
        // BFS depth >=1 processing

        // cnt of expanded states in previous iteration/depth
//        size_t cntTasksPreviousExpansion = tasksQueue.size();

            // iterate through states of previous expansion
//        for (size_t iterPrevExpansion = 0; iterPrevExpansion < cntTasksPreviousExpansion; iterPrevExpansion++) {
            // get task/state
            auto boardCurState = tasksQueue.front();
            // remove it from queue
            tasksQueue.pop_front();

            // change state: do move action on board
            boardCurState.moveActiveChessPieceToNextPos();

            // conditions scope:
            // check if enemies count isn't zero and in case yes try to update curUpperBoundDepth and curBestSolutionMovingHistory
            // also check if was already found best solution
            if (boardCurState.getActualEnemiesCnt() == 0) {
                tryToUpdateSolution(boardCurState, false);
                if (isFoundBestPossibleSolution()) break;
            } else {
                // add all children states of current state/task to queue
                for (auto nextPriorPosition: boardCurState.getNextOrderedByVal()) {
                    boardCurState.setNextPosToMove(nextPriorPosition);
                    tasksQueue.push_back(boardCurState);
                }
            }
//        }
    }
    return tasksQueue;
}

/**
 * Main function responsible for processing and solving problems
 */
void Solver::solve() {
    // Start time recording
    clock.startTime();

    // my_rank: rank of the calling process
    // number_of_processes: number of processes
    int my_rank, number_of_processes;
    MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &number_of_processes);

    // 1. MASTER_PROCESS________________________________________________________________________________________________
    if (my_rank == 0) {
        // do BFS expansion, returns  queue Chessboard states; cnt of tasks to expand: number_of_slaves * constant (for example 2)
        std::deque<Chessboard> tasksQueue = expandBFS(*problemToSolve->getChessboard(), (number_of_processes - 1) * 2);
        size_t cntOfExpandedTasksForSlaves = tasksQueue.size();
        size_t cntOfResponsesToWait = cntOfExpandedTasksForSlaves;

        // init vector of slaves busyness (default all set to true = free)
        std::vector<bool> freeSlaves(number_of_processes - 1, true);

        // send all generated tasks to free (not busy) SLAVES
        while (!tasksQueue.empty()) {
            auto freeSlaveIter = std::find(freeSlaves.begin(), freeSlaves.end(), true);

            if (freeSlaveIter != freeSlaves.end()) {
                auto freeSlaveNum = freeSlaveIter - freeSlaves.begin() + 1;

                // unwrap new task
                auto boardState = tasksQueue.front();
                tasksQueue.pop_front();

                // serialize board to MPI message
                MpiBoardMessage serializedBoard = boardState.serialize();
                // propagate master's (current) upper bound to slaves with new state
                serializedBoard.currentUpperBound = curUpperBoundDepth;

                // send serialized board to slave and set him at vector as busy
                MPI_Send(&serializedBoard, sizeof(struct MpiBoardMessage), MPI_PACKED, freeSlaveNum, 0, MPI_COMM_WORLD);
                // mark this slave as busy
                freeSlaves[freeSlaveNum - 1] = false;

            } else {
                MpiSlaveSolutionMessage slaveResponseMessage = MpiSlaveSolutionMessage();
                MPI_Status status;

                // blocking receive
                MPI_Recv(&slaveResponseMessage, sizeof(struct MpiSlaveSolutionMessage), MPI_PACKED, MPI_ANY_SOURCE, 0, MPI_COMM_WORLD,
                         &status);

                // mark this slave as free
                freeSlaves[status.MPI_SOURCE-1] = true;
                cntOfResponsesToWait--;

                // deserialize and try to update current solution
                deserializeSlaveMessageAndTryToUpdateMaster(slaveResponseMessage);
            }
        }

        // obtain all remaining responses from slaves
        for (size_t i = 0; i < cntOfResponsesToWait; i++) {
            MpiSlaveSolutionMessage slaveResponseMessage = MpiSlaveSolutionMessage();

            // blocking receive
            MPI_Recv(&slaveResponseMessage, sizeof(struct MpiSlaveSolutionMessage), MPI_PACKED, MPI_ANY_SOURCE, 0, MPI_COMM_WORLD,MPI_STATUS_IGNORE);

            // deserialize and try to update current solution
            deserializeSlaveMessageAndTryToUpdateMaster(slaveResponseMessage);
        }

        // stop all slaves (send stop message to all SLAVES)
        for (int slave_num = 1; slave_num < number_of_processes; slave_num++) {
            MpiBoardMessage masterMessage = MpiBoardMessage();
            // stop all slaves
            masterMessage.keepRunningSlave = false;
            // blocking send
            MPI_Send(&masterMessage, sizeof(struct MpiBoardMessage), MPI_PACKED, slave_num, 0, MPI_COMM_WORLD);
        }
    }
    // 2. SLAVE_PROCESS_________________________________________________________________________________________________
    else {

        while (true) {
            // blocking receive
            MpiBoardMessage masterMessage = MpiBoardMessage();
            MPI_Recv(&masterMessage, sizeof(struct MpiBoardMessage), MPI_PACKED, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

            if (!masterMessage.keepRunningSlave) {
                break;
            }

            // propagation of new upper bound to slaves
            if (masterMessage.currentUpperBound < curUpperBoundDepth) {
                curUpperBoundDepth = masterMessage.currentUpperBound;
            }

            auto boardState = Chessboard::deserialize(masterMessage);

            // IMPORTANT NOTICE: number of thread can be set whether OMP_NUM_THREADS (env var) or num_threads(8)
            // number of tasks to expand = MAX_NUMBER_OF_THREADS * CONSTANT (for example 22)
            size_t numberOfTasksToExpand = omp_get_num_threads() * 22;
            std::deque<Chessboard> tasksQueue = expandBFS(boardState, numberOfTasksToExpand, false);

            // move all task from queue to vector
            std::vector<Chessboard> tasksVector(tasksQueue.begin(), tasksQueue.end());
            tasksQueue.clear();

            // chunk size is tasks count divided by number of threads: chunk_size = (int)tasksVector.size() / omp_get_max_threads()
            // schedule(dynamic, chunk_size)
            #pragma omp parallel for shared(tasksVector) default(none) schedule(auto)
            for (size_t indx = 0; indx < tasksVector.size(); indx++) {
                if (!isFoundBestPossibleSolution()) {
                    solveDFSChessboard(tasksVector[indx]);
                }
            }

            // wrap solution to message
            MpiSlaveSolutionMessage solutionMessage = createSlaveSolutionMessage();
            // reset value of recCallsCnt for current SLAVE
            recCallsCnt = 0;
            // blocking send
            MPI_Send(&solutionMessage, sizeof(struct MpiSlaveSolutionMessage), MPI_PACKED, 0, 0, MPI_COMM_WORLD);
        }
    }

    // Stop time recording
    clock.stopTime();

    // save solution only to MASTER
    if (my_rank == 0) {
        problemToSolve->setSolution(new Solution(
                clock.getTimeInMilliseconds(),
                curUpperBoundDepth,
                recCallsCnt,
                curBestSolutionMovingHistory
        ));
    }
}

/**
 * Recursive function that trying to find the shortest sequence of moves to remove all enemies pieces on board
 * @param board indicates chessboard state for current depth
 * @param posToMove
 * @param curDepth
 * @return
 */
void Solver::solveDFSChessboard(Chessboard board) {
    // increment counter
    #pragma omp atomic update
    recCallsCnt++;

    // update chessboard state
    board.moveActiveChessPieceToNextPos();

    if (board.getActualEnemiesCnt() == 0) {
        tryToUpdateSolution(board, true);
        return;
    }

    // return in cases:
    // - is found best possible solution or
    // - conditions for min actual depth are not met
    if (board.getMovingHistorySize() + board.getActualEnemiesCnt() >= curUpperBoundDepth || isFoundBestPossibleSolution()) return;

    for(auto nextPriorPosition: board.getNextOrderedByVal()) {
        // do fast forward check; comment out this line to see clear recursive behavior of DFS
        if ((board.getMovingHistorySize() + 1) + board.getFastForwardEnemiesCntForPos(nextPriorPosition) >= curUpperBoundDepth) {
            continue;
        }

        // set next position to move
        board.setNextPosToMove(nextPriorPosition);

        // go deeper to recursion
        solveDFSChessboard(board);

        // return if best solution was found
        if (isFoundBestPossibleSolution()) return;
    }
}

// MPI_SCOPE_____________________________________________________________________
/**
 * The function is used to create a message/pack a task for a slave
 * @return
 */
MpiSlaveSolutionMessage Solver::createSlaveSolutionMessage() const {
    // wrap solution to message
    MpiSlaveSolutionMessage solutionMessage = MpiSlaveSolutionMessage();
    solutionMessage.price = curUpperBoundDepth;
    solutionMessage.recCallsCnt = recCallsCnt;

    solutionMessage.movingHistorySize = curBestSolutionMovingHistory.size();
    for (size_t indx = 0; indx < curBestSolutionMovingHistory.size(); indx++) {
        solutionMessage.movingHistory_X[indx] = curBestSolutionMovingHistory[indx].first;
        solutionMessage.movingHistory_Y[indx] = curBestSolutionMovingHistory[indx].second;
    }
    return solutionMessage;
}

/**
 * The function serves to deserialize the message from slave, and further, if the conditions are met, update the current solution
 * @param message
 */
void Solver::deserializeSlaveMessageAndTryToUpdateMaster(MpiSlaveSolutionMessage &message) {
    // update solution
    recCallsCnt += message.recCallsCnt;
    // if slave have found solution and its price is better than current one.
    if (message.movingHistorySize != 0 && curUpperBoundDepth > message.price) {
        curUpperBoundDepth = message.price;

        // deserialize moving history from SLAVE
        std::vector<Coord_t> movingHistoryFromSlave;
        movingHistoryFromSlave.reserve(message.price);
        for (auto indx = 0; indx < message.price; indx++) {
            movingHistoryFromSlave.emplace_back(
                    Coord_t(message.movingHistory_X[indx], message.movingHistory_Y[indx])
            );
        }
        curBestSolutionMovingHistory = movingHistoryFromSlave;
    }
}

//
// Created by Mykyta on 01/03/2021.
//

#pragma once

#include <chrono>

class Clock {
private:
    std::chrono::steady_clock::time_point start;
    std::chrono::steady_clock::time_point end;

public:
    Clock();
    void startTime();
    void stopTime();

    int getTimeInNanoseconds() const;
    int getTimeInMicroseconds() const;
    int getTimeInMilliseconds() const;
    int getTimeInSeconds() const;
};



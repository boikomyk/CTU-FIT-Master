//
// Created by Mykyta on 01/03/2021.
//

#include "Clock.h"

Clock::Clock() = default;

void Clock::startTime() {
    this->start = std::chrono::steady_clock::now();
}

void Clock::stopTime() {
    this->end = std::chrono::steady_clock::now();
}

int Clock::getTimeInNanoseconds() const {
    return std::chrono::duration_cast<std::chrono::nanoseconds>(end - start).count();
}

int Clock::getTimeInMicroseconds() const {
    return std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
}

int Clock::getTimeInMilliseconds() const {
    return std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
}

int Clock::getTimeInSeconds() const {
    return std::chrono::duration_cast<std::chrono::seconds>(end - start).count();
}

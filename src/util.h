#pragma once
#include <string>
#include <vector>

std::vector<std::string> shlex(std::string s);

std::string replaceall(const std::string &str, const std::string &from,
                       const std::string &to);

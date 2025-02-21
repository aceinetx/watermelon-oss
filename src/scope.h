#pragma once
#include <string>
#include <map>

typedef struct {
	double value_d;
	std::string value_s;
} Variable;

typedef struct {
	std::map<std::string, Variable> variables;
} Scope;

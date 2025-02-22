#pragma once
#include <map>
#include <string>
#include <vector>

#include "lexer.h"
#include "scope.h"

typedef enum IfStCond { Eq, NEq, More, Less, MoreEq, LessEq } IfStCond;

typedef struct IfSt {
	std::string var;
	std::string equal;
	bool active;
	bool elsecon;
	IfStCond condition;
} IfSt;

class Parser {
private:
	std::vector<Token> tokens;
	std::vector<IfSt> ifst;
	bool toexit;

public:
	std::map<std::string, Scope> scopes;
	std::string current_scope;
	Parser();
	~Parser();
	void run(std::vector<Token> tokens);
};

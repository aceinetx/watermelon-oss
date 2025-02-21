#pragma once
#include "lexer.h"
#include <vector>
#include "scope.h"
#include <map>

class Parser {
	private:
std::vector<Token> tokens;
	public:
		std::map<std::string, Scope> scopes;
		std::string current_scope;
		Parser();
		void run(std::vector<Token> tokens);
};

#include "parser.h"
#include <format>

Parser::Parser(){
	scopes["essential"] = Scope { {} };
	scopes["global"] = Scope { {} };

	for(int i=0; i<=10; i++){
		scopes["essential"].variables[std::format("arg{}", i)] = {0, ""};
	}
};

void Parser::run(std::vector<Token> _tokens){
	long c = 0;
	bool end = false;
	bool iscomment = false;
	bool func_def = false;
	bool skip_until_loop_end = false;
	tokens = _tokens;

	while(c < tokens.size()){
		std::map<std::string, Variable> variables = scopes[current_scope].variables;
		if(current_scope != "global"){
			for(auto const& [key, value] : scopes["global"].variables){
				variables[key] = value;
			}
		}
		for(auto const& [key, value] : scopes["essential"].variables){
			variables[key] = value;
		}

		if(tokens[c].name == "CommentEnd"): iscomment = false;

		if(iscomment){
			c++;
			continue;
		}

		if(tokens[c].name == "KEndLoop"){
			if(skip_until_loop_end){
				c++;
				continue;
			}
		} else {
			if(skip_until_loop_end){
				skip_until_loop_end = false;
			}
		}

		if(toexit == true) break;

		if(tokens[c].name == "End"){
			end = false;
		} else if (tokens[c].name == "STend"){
			if(ifst.size() > 0){
				ifst.pop_back(); // NOTE: I'm not sure that this will do the same effect as in python
			}
		} else if(tokens[c].name == "STelse"){
			// TODO
		}


	}
}

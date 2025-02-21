#pragma once
#include <string>
#include <vector>

typedef struct {
  std::string name;
  std::string value;
} Token;

class Lexer {
private:
  std::string code;

public:
  Lexer();
  std::vector<Token> tokenize(std::string code);
};

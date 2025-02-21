#pragma once
#include <string>

typedef struct {
  std::string name;
  std::string value;
} Token;

class Lexer {
private:
  std::string code;

public:
  Lexer();
  void tokenize(std::string code);
};

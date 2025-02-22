#include "lexer.h"
#include "parser.h"
#include <iostream>

int main(int argc, char **argv) {
  Lexer lexer;
  std::vector<Token> tokens = lexer.tokenize("fn main; nf;");
  for (Token &token : tokens) {
    std::cout << token.value << " ";
  }
  std::cout << std::endl;

  Parser parser;
  parser.run(tokens);
  return 0;
}

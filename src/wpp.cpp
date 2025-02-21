#include "lexer.h"
#include <iostream>

int main(int argc, char **argv) {
  Lexer lexer;
  lexer.tokenize("fn main; nf;");
  return 0;
}

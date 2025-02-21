#include "lexer.h"
#include "util.h"
#include <regex>

Lexer::Lexer() = default;
void Lexer::tokenize(std::string code) {
  this->code = code;
  this->code = replaceall(this->code, ";", " ;");
  this->code = replaceall(this->code, "X[E0", ";");
  this->code = replaceall(this->code, "\n", "\x01\n");

  std::vector<std::string> src = shlex(this->code);
  std::vector<Token> tokens = {};

  for (std::string _word : src) {
    std::string word = _word;
    bool newline = false;
    if (_word.back() == '\x01') {
      newline = true;
      word.pop_back();
    }

    if (word.size() == 0) {
      word = "\x00";
    }

    if (word == "println" || word == "print") {
      tokens.append({"KOut", word});
    } else if (word == "scanln") {
      tokens.append({"KInput", word});
    } else if (word == "var") {
      tokens.append({"KVal", word});
    } else if (word == "return") {
      tokens.append({"KReturn", word});
    } else if (word == "free") {
      tokens.append({"KFree", word});
    } else if (word == "fn") {
      tokens.append({"KFn", word});
    } else if (word == "len") {
      tokens.append({"KLen", word});
    } else if (word == "getchar") {
      tokens.append({"KGetChar", word});
    } else if (word == "setchar") {
      tokens.append({"KSetChar", word});
    } else if (word == "nf") {
      tokens.append({"KIndentEnd", word});
    } else if (word == "call") {
      tokens.append({"KFnCall", word});
    } else if (word == "namespace") {
      tokens.append({"KNamespace", word});
    } else if (word == "nsEnd") {
      tokens.append({"KNamespaceEnd", word});
    } else if (word == "exit") {
      tokens.append({"KExit", word});
    } else if (word == "loop") {
      tokens.append({"KLoop", word});
    } else if (word == "break") {
      tokens.append({"KBreak", word});
    } else if (word == "lend") {
      tokens.append({"KEndLoop", word});
    } else if (word == "sleep") {
      tokens.append({"KSleep", word});
    } else if (word == "utime") {
      tokens.append({"KUTime", word});
    } else if (word == "cp") {
      tokens.append({"KCopy", word});
    } else if (word == "?") {
      tokens.append({"KComment", word});
    } else if (word == "-?") {
      tokens.append({"KCommentEnd", word});
    } else if (word == "none") {
      tokens.append({"KNone", word});
    } else if (word == "true" || word == "false") {
      tokens.append({"KBool", word});
    } else if (word[0] == '"' && word.back() == '"') {
      std::string temp = word;
      temp.pop_back();
      temp.erase(temp.begin());
      tokens.append({"TStr", temp});
    } else if (word == "if") {
      tokens.append({"STif", word});
    } else if (word == "else") {
      tokens.append({"STelse", word});
    } else if (word == "end") {
      tokens.append({"STend", word});
    } else if (std::regex_match("[a-z]", word) ||
               std::regex_match("[A-Z]", word)) {
      tokens.append({"Identifier", word});
    } else if (word == ";") {
      tokens.append({"End", word});
    } else if (std::regex_match("[+\-=*/]", word)) {
      tokens.append({"Op", word});
    } else if (word == "==") {
      tokens.append({"Eq", word});
    } else if (word == "!=") {
      tokens.append({"NEq", word});
    } else if (word == ">") {
      tokens.append({"More", word});
    } else if (word == "<") {
      tokens.append({"Less", word});
    } else if (word == ">=") {
      tokens.append({"MoreEq", word});
    } else if (word == "<=") {
      tokens.append({"LessEq", word});
    } else {
      if (std::regex_match("[+-]?([0-9]*[.])?[0-9]+", word)) {
        tokens.append({"TFloat", word});
      } else if (std::regex_match("[0-9]", word)) {
        tokens.append({"TInt", word});
      } else {
        tokens.append({"Indentifier", word});
      }
    }
  }
}

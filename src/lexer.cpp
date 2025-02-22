#include "lexer.h"
#include "util.h"
#include <regex>

Lexer::Lexer() = default;
std::vector<Token> Lexer::tokenize(std::string code) {
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
      tokens.push_back({"KOut", word});
    } else if (word == "scanln") {
      tokens.push_back({"KInput", word});
    } else if (word == "var") {
      tokens.push_back({"KVal", word});
    } else if (word == "return") {
      tokens.push_back({"KReturn", word});
    } else if (word == "free") {
      tokens.push_back({"KFree", word});
    } else if (word == "fn") {
      tokens.push_back({"KFn", word});
    } else if (word == "len") {
      tokens.push_back({"KLen", word});
    } else if (word == "getchar") {
      tokens.push_back({"KGetChar", word});
    } else if (word == "setchar") {
      tokens.push_back({"KSetChar", word});
    } else if (word == "nf") {
      tokens.push_back({"KIndentEnd", word});
    } else if (word == "call") {
      tokens.push_back({"KFnCall", word});
    } else if (word == "namespace") {
      tokens.push_back({"KNamespace", word});
    } else if (word == "nsEnd") {
      tokens.push_back({"KNamespaceEnd", word});
    } else if (word == "exit") {
      tokens.push_back({"KExit", word});
    } else if (word == "loop") {
      tokens.push_back({"KLoop", word});
    } else if (word == "break") {
      tokens.push_back({"KBreak", word});
    } else if (word == "lend") {
      tokens.push_back({"KEndLoop", word});
    } else if (word == "sleep") {
      tokens.push_back({"KSleep", word});
    } else if (word == "utime") {
      tokens.push_back({"KUTime", word});
    } else if (word == "cp") {
      tokens.push_back({"KCopy", word});
    } else if (word == "?") {
      tokens.push_back({"KComment", word});
    } else if (word == "-?") {
      tokens.push_back({"KCommentEnd", word});
    } else if (word == "none") {
      tokens.push_back({"KNone", word});
    } else if (word == "true" || word == "false") {
      tokens.push_back({"KBool", word});
    } else if (word[0] == '"' && word.back() == '"') {
      std::string temp = word;
      temp.pop_back();
      temp.erase(temp.begin());
      tokens.push_back({"TStr", temp});
    } else if (word == "if") {
      tokens.push_back({"STif", word});
    } else if (word == "else") {
      tokens.push_back({"STelse", word});
    } else if (word == "end") {
      tokens.push_back({"STend", word});
    } else if (std::regex_match(word, std::regex("[a-z]")) ||
	       std::regex_match(word, std::regex("[A-Z]"))) {
      tokens.push_back({"Identifier", word});
    } else if (word == ";") {
      tokens.push_back({"End", word});
    } else if (std::regex_match(word, std::regex("[+\\-=*/]"))) {
      tokens.push_back({"Op", word});
    } else if (word == "==") {
      tokens.push_back({"Eq", word});
    } else if (word == "!=") {
      tokens.push_back({"NEq", word});
    } else if (word == ">") {
      tokens.push_back({"More", word});
    } else if (word == "<") {
      tokens.push_back({"Less", word});
    } else if (word == ">=") {
      tokens.push_back({"MoreEq", word});
    } else if (word == "<=") {
      tokens.push_back({"LessEq", word});
    } else {
      if (std::regex_match(word, std::regex("[+-]?([0-9]*[.])?[0-9]+"))) {
	tokens.push_back({"TFloat", word});
      } else if (std::regex_match(word, std::regex("[0-9]"))) {
	tokens.push_back({"TInt", word});
      } else {
	tokens.push_back({"Indentifier", word});
      }
    }
  }

  return tokens;
}

#pragma once
#include <map>
#include <string>

typedef struct Variable {
  union {
    double d;
    std::string *s;
  };
  bool isString();
  Variable(double d = 0, std::string s = "");
  ~Variable();
} Variable;

typedef struct {
  std::map<std::string, Variable> variables;
} Scope;

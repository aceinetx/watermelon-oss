#pragma once
#include <map>
#include <string>

typedef enum VarTypes {
  VarNum,
  VarStr,
};

typedef struct Variable {
  double d;
  std::string s;
} Variable;

typedef struct {
  std::map<std::string, Variable> variables;
} Scope;

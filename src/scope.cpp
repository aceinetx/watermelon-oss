#include "scope.h"
#include <typeinfo>
#include <iostream>

bool Variable::isString() {
  if (std::string(typeid(this->s).name()).find("string") != std::string::npos) {
    return true;
  }
  return false;
}
Variable::Variable(double d, std::string s) {
  this->s = new std::string(s);
  this->d = d;
	std::cout << "var alloc\n";
}
Variable::~Variable() {
  delete this->s;
	std::cout << "var free\n";
}

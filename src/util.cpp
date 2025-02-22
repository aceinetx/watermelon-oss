#include "util.h"
#include <sstream>

std::vector<std::string> shlex(std::string s) {
  std::vector<std::string> tokens;
  std::string token;
  std::istringstream stream(s);
  bool in_quotes = false;
  char quote_char = '\0';

  while (stream) {
    char c = stream.get();
    if (stream.eof())
      break;

    if (c == '"' || c == '\'') {
      if (in_quotes && c == quote_char) {
	// Closing the quote
	in_quotes = false;
	quote_char = '\0';
      } else if (!in_quotes) {
	// Opening a quote
	in_quotes = true;
	quote_char = c;
      } else {
	// Inside quotes, just add the character to the token
	token += c;
      }
    } else if (isspace(c)) {
      if (in_quotes) {
	// Inside quotes, just add the character to the token
	token += c;
      } else {
	if (!token.empty()) {
	  tokens.push_back(token);
	  token.clear();
	}
      }
    } else {
      // Regular character, add to token
      token += c;
    }
  }

  // Add the last token if it exists
  if (!token.empty()) {
    tokens.push_back(token);
  }

  return tokens;
}

std::string replaceall(const std::string &str, const std::string &from,
		       const std::string &to) {
  if (from.empty())
    return str; // Avoid empty substring case

  std::string result = str; // Create a copy of the original string
  size_t start_pos = 0;
  while ((start_pos = result.find(from, start_pos)) != std::string::npos) {
    result.replace(start_pos, from.length(), to);
    start_pos += to.length(); // Move past the replaced part
  }
  return result; // Return the modified string
}

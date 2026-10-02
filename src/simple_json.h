#pragma once
#include <string>
#include <vector>
#include <map>
#include <sstream>
#include <cctype>
#include <cstdlib>
#include <stdexcept>

namespace simple_json {

enum Type {
    kNull,
    kBool,
    kNumber,
    kString,
    kArray,
    kObject
};

struct Value {
    Type type = kNull;
    bool bool_val = false;
    double num_val = 0.0;
    std::string str_val;
    std::vector<Value> arr_val;
    std::map<std::string, Value> obj_val;

    Value() : type(kNull) {}
    Value(bool b) : type(kBool), bool_val(b) {}
    Value(double d) : type(kNumber), num_val(d) {}
    Value(int i) : type(kNumber), num_val(i) {}
    Value(const char* s) : type(kString), str_val(s) {}
    Value(const std::string& s) : type(kString), str_val(s) {}

    bool is_null() const { return type == kNull; }
    bool is_bool() const { return type == kBool; }
    bool is_number() const { return type == kNumber; }
    bool is_string() const { return type == kString; }
    bool is_array() const { return type == kArray; }
    bool is_object() const { return type == kObject; }

    bool as_bool(bool def = false) const { return is_bool() ? bool_val : def; }
    double as_float(double def = 0.0) const { return is_number() ? num_val : def; }
    int as_int(int def = 0) const { return is_number() ? (int)num_val : def; }
    const std::string& as_string(const std::string& def = "") const { return is_string() ? str_val : def; }
    const std::vector<Value>& as_array() const { static std::vector<Value> empty; return is_array() ? arr_val : empty; }
    const std::map<std::string, Value>& as_object() const { static std::map<std::string, Value> empty; return is_object() ? obj_val : empty; }

    bool contains(const std::string& k) const {
        return is_object() && obj_val.find(k) != obj_val.end();
    }

    const Value& operator[](const std::string& k) const {
        static Value null_val;
        if (!is_object()) return null_val;
        auto it = obj_val.find(k);
        return it != obj_val.end() ? it->second : null_val;
    }

    Value& operator[](const std::string& k) {
        if (type != kObject) {
            type = kObject;
            obj_val.clear();
        }
        return obj_val[k];
    }

    void push_back(const Value& v) {
        if (type != kArray) {
            type = kArray;
            arr_val.clear();
        }
        arr_val.push_back(v);
    }

    std::string dump() const {
        std::ostringstream ss;
        write_stream(ss);
        return ss.str();
    }

private:
    void write_stream(std::ostream& os) const {
        switch (type) {
            case kNull: os << "null"; break;
            case kBool: os << (bool_val ? "true" : "false"); break;
            case kNumber: {
                if (num_val == (long long)num_val) os << (long long)num_val;
                else {
                    char buf[32];
                    snprintf(buf, sizeof(buf), "%.6g", num_val);
                    os << buf;
                }
                break;
            }
            case kString: {
                os << '"';
                for (char c : str_val) {
                    if (c == '"') os << "\\\"";
                    else if (c == '\\') os << "\\\\";
                    else if (c == '\n') os << "\\n";
                    else if (c == '\r') os << "\\r";
                    else if (c == '\t') os << "\\t";
                    else os << c;
                }
                os << '"';
                break;
            }
            case kArray: {
                os << '[';
                for (size_t i = 0; i < arr_val.size(); ++i) {
                    if (i > 0) os << ',';
                    arr_val[i].write_stream(os);
                }
                os << ']';
                break;
            }
            case kObject: {
                os << '{';
                bool first = true;
                for (const auto& kv : obj_val) {
                    if (!first) os << ',';
                    first = false;
                    os << '"' << kv.first << "\":";
                    kv.second.write_stream(os);
                }
                os << '}';
                break;
            }
        }
    }
};

class Parser {
    const std::string& src;
    size_t pos;

    void skip_whitespace() {
        while (pos < src.size() && (std::isspace((unsigned char)src[pos]) || src[pos] == '\0')) {
            pos++;
        }
    }

    char peek() {
        skip_whitespace();
        return pos < src.size() ? src[pos] : '\0';
    }

    char get() {
        skip_whitespace();
        return pos < src.size() ? src[pos++] : '\0';
    }

    std::string parse_string() {
        if (get() != '"') return "";
        std::string s;
        while (pos < src.size()) {
            char c = src[pos++];
            if (c == '"') break;
            if (c == '\\' && pos < src.size()) {
                char esc = src[pos++];
                if (esc == '"') s += '"';
                else if (esc == '\\') s += '\\';
                else if (esc == '/') s += '/';
                else if (esc == 'b') s += '\b';
                else if (esc == 'f') s += '\f';
                else if (esc == 'n') s += '\n';
                else if (esc == 'r') s += '\r';
                else if (esc == 't') s += '\t';
                else s += esc;
            } else {
                s += c;
            }
        }
        return s;
    }

    Value parse_number() {
        size_t start = pos;
        if (pos < src.size() && (src[pos] == '-' || src[pos] == '+')) pos++;
        while (pos < src.size() && (std::isdigit((unsigned char)src[pos]) || src[pos] == '.' ||
                                   src[pos] == 'e' || src[pos] == 'E' || src[pos] == '-' || src[pos] == '+')) {
            pos++;
        }
        double d = std::atof(src.substr(start, pos - start).c_str());
        return Value(d);
    }

public:
    Parser(const std::string& input) : src(input), pos(0) {}

    Value parse() {
        skip_whitespace();
        char c = peek();
        if (c == '\0') return Value();
        if (c == '{') {
            get(); // eat '{'
            Value obj;
            obj.type = kObject;
            while (peek() != '}' && peek() != '\0') {
                std::string key = parse_string();
                skip_whitespace();
                if (get() != ':') break;
                Value val = parse();
                obj.obj_val[key] = val;
                if (peek() == ',') get();
            }
            if (peek() == '}') get();
            return obj;
        } else if (c == '[') {
            get(); // eat '['
            Value arr;
            arr.type = kArray;
            while (peek() != ']' && peek() != '\0') {
                Value val = parse();
                arr.arr_val.push_back(val);
                if (peek() == ',') get();
            }
            if (peek() == ']') get();
            return arr;
        } else if (c == '"') {
            return Value(parse_string());
        } else if (c == 't' || c == 'T') {
            pos += 4;
            return Value(true);
        } else if (c == 'f' || c == 'F') {
            pos += 5;
            return Value(false);
        } else if (c == 'n' || c == 'N') {
            pos += 4;
            return Value();
        } else {
            return parse_number();
        }
    }
};

inline Value parse(const std::string& json_str) {
    Parser p(json_str);
    return p.parse();
}

} // namespace simple_json

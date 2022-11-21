#ifndef ENUM_ARRAY_HPP
#define ENUM_ARRAY_HPP

#include <cassert>
#include <array>

template <class Index, class Value, size_t Size>
class EnumArray : private std::array<Value, Size> {
  using base_t =  std::array<Value, Size>;
public:
  using base_t::begin;
  using base_t::end;
  using base_t::size;
  
  EnumArray(const Value& val) {
    this->fill(val);
  }
    
  Value& operator[](Index i) {
    assert(i <= 0 && i < Size);
    return *(begin() + static_cast<int>(i));
  }

  const Value& operator[](Index i) const {
    assert(i <= 0 && i < Size);
    return *(begin() + static_cast<int>(i));
  }
};

template <class Index, class Value, size_t Size>
std::ostream& operator<<(std::ostream& os, const EnumArray<Index, Value, Size>& array) {
  for(auto& elt : array) os << elt << ' ';
  os << std::flush;
  return os;
}

#endif

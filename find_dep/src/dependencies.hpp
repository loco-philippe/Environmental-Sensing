#ifndef DEPENDENCIES_HPP
#define DEPENDENCIES_HPP

#include <stdexcept>
#include <unordered_map>
#include <unordered_set>

#include "enum_array.hpp"

namespace dependencies {
  
  enum class Link {
    derived = 0,
    deriving = 1,
    crossed = 2,
    coupled = 3,
    linked = 4
  };

  const char* c_str(Link link) {
    using enum Link;

    static const char* link_types[] = {"derived", "deriving", "crossed", "coupled", "linked" };
    return link_types[static_cast<int>(link)];
  }

  std::ostream& operator<<(std::ostream& os, const Link& link) {
    os << '(' << c_str(link) << ')';
    return os;
  }


  
  template<typename Map, typename Value2>
  std::pair<size_t, bool> find_count_and_insert(Map& map, const typename Map::key_type& val1, const Value2& val2) {
    auto& values = map[val1];
    auto [ _, insert ] = values.insert(val2);
    return { values.size(), insert};
  }

  
  
  template<typename Value1, typename Value2>
  class CrossDependency {
    using enum Link;

    std::unordered_map<Value1, std::unordered_set<Value2>> a_to_b_;
    std::unordered_map<Value2, std::unordered_set<Value1>> b_to_a_;
    EnumArray<Link, bool, 3> states_;
    size_t n_, n_states_;

    void disable(Link state) {
      if(states_[state]) {
	states_[state] = false;
	--n_states_;
      }
    }
    
  public:
    CrossDependency() : a_to_b_{}, b_to_a_{},
			states_{true},
			n_{} {
      n_states_ = states_.size();
    }

    void add(const Value1& val1, const Value2& val2) {
      auto [ val1_count, insert ] = find_count_and_insert(a_to_b_, val1, val2);
      
      if(insert) {
	if(val1_count > 1)
	  disable(deriving);
	
	auto [ val2_count, _ ] = find_count_and_insert(b_to_a_, val2, val1);
	if(val2_count > 1)
	  disable(derived);
      } else {	
	disable(crossed);
      }
      ++n_;
#ifdef DEBUG
      std::cout << states_ << std::endl;
#endif
    }

    operator bool() const {
      return n_states_ >= 1;
    }

    operator Link() const {
      if(n_states_ >= 1) {
	if(states_[crossed] && (n_ == a_to_b_.size() * b_to_a_.size())) return crossed;
	if(states_[derived]) {
	  if(states_[deriving])
	    return coupled;
	  else
	    return derived;
	} else
	  if(states_[deriving]) return deriving;
      }	
      return linked;
    }
  };
  
    
  template<typename Iterator1, typename Iterator2>
  Link find_dep(const Iterator1& a_begin, const Iterator1& a_end, const Iterator2& b_begin, const Iterator2& b_end) {
    Iterator1 it_a = a_begin;
    Iterator2 it_b = b_begin;
    using value1_t = typename Iterator1::value_type;
    using value2_t = typename Iterator2::value_type;

    CrossDependency<value1_t, value2_t> deps;
    for(; (it_a != a_end) && (it_b != b_end) && deps; ++it_a, ++it_b)
      deps.add(*it_a, *it_b);

    if(deps) {
      if(it_a != a_end) throw std::runtime_error("find: A is longer than B");
      if(it_b != b_end) throw std::runtime_error("find: B is longer than A");
    }
    return deps;
  }
}
#endif

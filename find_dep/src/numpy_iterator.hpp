#ifndef NUMPY_STD_ITERATOR_HPP
#define NUMPY_STD_ITERATOR_HPP
  
#include <numpy/arrayobject.h>

template<typename T>
class NumpyIterator {
  PyArrayIterObject* it_;
  
public:
  NumpyIterator() : it_() {}
  NumpyIterator(PyObject* array) : it_(reinterpret_cast<PyArrayIterObject *>(PyArray_IterNew(array))) {}
  NumpyIterator(const NumpyIterator& other) : it_(other.it_) {
    Py_XINCREF(it_);
  }
  ~NumpyIterator() {
    Py_XDECREF(it_);
  }

  using value_type = T;
  
  const T& operator*() const {
    const T* data = static_cast<const T*>(PyArray_ITER_DATA(it_));
    return *data;
  }

  T& operator*() {
    T* data = static_cast<T*>(PyArray_ITER_DATA(it_));
    return *data;
  }

  NumpyIterator& operator++() {
    PyArray_ITER_NEXT(it_);
    if(! PyArray_ITER_NOTDONE(it_)) it_ = nullptr;
    return *this;
  }
  
  bool operator!=(const NumpyIterator<T>& other) const {
    return !(*this == other);
  }
  
  bool operator==(const NumpyIterator<T>& other) const {
    if(it_ == nullptr) return other.it_ == nullptr;
    else if(other.it_ == nullptr) return false;
    else {
      const T* data1 = static_cast<const T*>(PyArray_ITER_DATA(it_));
      const T* data2 = static_cast<const T*>(PyArray_ITER_DATA(other.it_));
      return data1 == data2;
    }
  }
};

template<typename T>
class NumpyArray {
  PyObject* array_;  
public:
  NumpyArray(PyObject* array) : array_(array) {
    Py_XINCREF(array_);
  }
  
  ~NumpyArray() {
    Py_XDECREF(array_);
  }
  
  using iterator = NumpyIterator<T>;

  iterator begin() { return iterator(array_); }
  iterator end() { return iterator(); }
};



#endif

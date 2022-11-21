#include <Python.h>
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>

#include <iostream>
#include "numpy_iterator.hpp"
#include "dependencies.hpp"

#define ARRAY_TYPE NPY_LONG

#if ARRAY_TYPE == NPY_LONG
using array_value_t = long;
#else
#error "Unsupported value type"
#endif

static PyObject* find_dependencies(PyObject *dummy, PyObject *args)
{
    PyObject *arg1 = nullptr, *arg2 = nullptr;
    PyObject *arr1 = nullptr, *arr2 = nullptr;
   
    if (!PyArg_ParseTuple(args, "OO", &arg1, &arg2)) return nullptr;
    arr1 = PyArray_FROM_OTF(arg1, ARRAY_TYPE, NPY_ARRAY_IN_ARRAY);   
    arr2 = PyArray_FROM_OTF(arg2, ARRAY_TYPE, NPY_ARRAY_IN_ARRAY);
    
    if (arr1 != nullptr && arr2 != nullptr) {
      using namespace dependencies;
      
      NumpyArray<array_value_t> A1(arr1), A2(arr2);      
      Link link = find_dep(A1.begin(), A1.end(), A2.begin(), A2.end());
        
      PyObject* res = Py_BuildValue("s", c_str(link));

      Py_DECREF(arr1);
      Py_DECREF(arr2);
      return res;
    }  else {
      Py_XDECREF(arr1);
      Py_XDECREF(arr2);
      return nullptr;
    }
}


static PyMethodDef FinddepMethods[] = {
  {"find_dep", find_dependencies, METH_VARARGS, "Identify dependencies between two numpy integer 1D arrays."},
  {nullptr, nullptr, 0, nullptr}        /* Sentinel */
};


static const char finddep_doc[] = "This is the doc";

static struct PyModuleDef finddepmodule = {
  PyModuleDef_HEAD_INIT,
  "finddep",   /* name of module */
  finddep_doc, /* module documentation, may be nullptr */
  -1,       /* size of per-interpreter state of the module,
	       or -1 if the module keeps state in global variables. */
  FinddepMethods
};

static PyObject *FinddepError;

extern "C" {
  PyMODINIT_FUNC PyInit_finddep() {
    PyObject *m;

    m = PyModule_Create(&finddepmodule);
    if (m == nullptr)
      return nullptr;

    FinddepError = PyErr_NewException("finddep.error", nullptr, nullptr);
    Py_XINCREF(FinddepError);
    if (PyModule_AddObject(m, "error", FinddepError) < 0) {
      Py_XDECREF(FinddepError);
      Py_CLEAR(FinddepError);
      Py_DECREF(m);
      return nullptr;
    }
  
    import_array();
    return m;
  }

}

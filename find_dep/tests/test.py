import numpy as np
import time, sys, argparse
import unittest
import finddep as fd

class SimpleTest(unittest.TestCase):

    def simple_test(self, link_type, generator):
        a,b = generator()
        res = fd.find_dep(a,b)
        self.assertEqual(res, link_type)
        
    def test_derived(self):
        return self.simple_test("derived", lambda : ( [1,2,1,2,2,1], [1,2,3,4,5,6] ))
    
    def test_deriving(self):
        return self.simple_test("deriving", lambda : ( [1,2,3,4,5,6], [1,2,1,2,2,1] ))
    
    def test_coupled(self):
        return self.simple_test("coupled", lambda : ( [1,2,3,4,5,6], [6,5,4,3,2,1] ))
    
    def test_crossed(self):
        return self.simple_test("crossed", lambda : ( [1,2,3,1,2,3], [1,1,1,2,2,2] ))
    
    def test_linked(self):
        return self.simple_test("linked", lambda : ( [1,1,2,2,1,1], [3,3,3,5,3,3] ))


def python_implementation(a,b):
    dist = len(set(zip(a,b)))
    la, lb = len(set(a)), len(set(b))
    if dist == lb and dist > la:
        return "derived"
    elif dist == la and dist > lb:
        return "deriving"
    elif dist == la and dist == lb:
        return "coupled"
    elif dist == la * lb:
        return "crossed"
    else:
        return "linked"

    
class PerformanceTest(unittest.TestCase):
    n_samples = 1000
    n_values  = 100
    
    def processing_time(self, f, dt_min=.1):
        n_runs = 1    
        while(True):
            t_start = time.time()
            for _ in range(n_runs):
                f()
            dt = time.time() - t_start
            if dt >= dt_min:
                break
            else:
                n_runs = int(dt_min / dt * n_runs) + 1
        return dt / n_runs

    def run_performance_test(self, a, b, name):
        dt_cpp = self.processing_time(lambda : fd.find_dep(a,b))
        dt_python = self.processing_time(lambda : python_implementation(a,b))
        print('acceleration ratio = {:6.1f} for {} {} arrays'.format(dt_python/dt_cpp, self.n_samples, name))
        return dt_cpp, dt_python

    def test_random_arrays(self):
        n, k = self.n_samples, self.n_values
        a = np.random.randint(low=0, high=k, size=(n,))
        b = np.random.randint(low=0, high=k, size=(n,))
        self.run_performance_test(a, b, 'random')

    def test_coupled_arrays(self, n=1000, k=10):
        n, k = self.n_samples, self.n_values
        a = np.random.randint(low=0, high=k, size=(n,))
        self.run_performance_test(a, a, 'coupled')

    def test_derived_arrays(self, n=1000, k=10):
        n, k = self.n_samples, self.n_values
        a = np.random.randint(low=0, high=k, size=(n,))
        b = np.ones((n,), dtype=int)
        self.run_performance_test(a, b, 'derived')
        
    def test_crossed_arrays(self, n=1000, k=10):
        n, ka = self.n_samples, self.n_values
        kb = int(n/ka) + 1
        a = [ x for x in range(ka) ] * kb
        b = sum([ [x] * ka for x in range(kb) ], [])
        a = np.array(a, dtype=int)
        b = np.array(b, dtype=int)
        self.run_performance_test(a, b, 'crossed')
        

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--n', type=int, default=10000, help='number of samples')
    parser.add_argument('--k', type=int, default=100, help='number of random values')
    res, args = parser.parse_known_args(sys.argv)
    PerformanceTest.n_samples = res.n
    PerformanceTest.n_values = res.k
    return args

if __name__ == "__main__":
    remaining_args = parse_args()
    unittest.main(argv=remaining_args, verbosity=0)
    

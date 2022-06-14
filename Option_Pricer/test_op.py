import unittest
from op import _gbs
from op import GBS_InputException

_DEBUG = False

def _debug(debug_input):
    if (__name__ == "__main__") and (_DEBUG == True):
        print(debug_input)

# This function tests that two floating point numbers are the same
# Numbers less than 1 million are considered the same if they are within .000001 of each other
# Numbers larger than 1 million are considered the same if they are within .0001% of each other
# User can override the default precision if necessary
def assert_close(value_a, value_b, precision=.000001):
    my_result = None

    if (value_a < 1000000.0) and (value_b < 1000000.0):
        my_diff = abs(value_a - value_b)
        my_diff_type = "Difference"
    else:
        my_diff = abs((value_a - value_b) / value_a)
        my_diff_type = "Percent Difference"

    _debug(f"Comparing {value_a} and {value_b}. Difference is {my_diff}, Difference Type is {my_diff_type}")

    if my_diff < precision:
        my_result = True
    else:
        my_result = False

    if (__name__ == "__main__") and (my_result == False):
        print(f"  FAILED TEST. Comparing {value_a} and {value_b}. Difference is {my_diff}, Difference Type is {my_diff_type}")
    else:
        print(".")

    return my_result

class testop(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.call_option_1 = ('c', 100, 95, 0.00273972602739726, 0.000751040922831883, 0, 0.2)
        self.call_option_2 = ('c', 92.45, 107.5, 0.0876712328767123, 0.00192960198828152, 0, 0.3)
        self.call_option_3 = ('c', 93.0766666666667, 107.75, 0.164383561643836, 0.00266390125346286, 0, 0.2878)
        self.call_option_4 = ('c', 100, 100, 1, 0.05, 0, 0.15)


        self.put_option_1 = ('p', 94.2666666666667, 107.75, 0.498630136986301, 0.00372609838856132, 0, 0.2888)
        self.put_option_2 = ('p', 94.3666666666667, 107.75, 0.583561643835616, 0.00370681407974257, 0, 0.2923)
        self.put_option_3 = ('p', 94.44, 107.75, 0.668493150684932, 0.00364163303865433, 0, 0.2908)
        self.put_option_4 = ('p', 100, 100, 1, 0.05, 0, 0.15)

    @classmethod
    def tearDownClass(cls):
        pass

    # Test exception throwing in inputs of _gbs() function
    def test_input(self):
        self.assertRaises(GBS_InputException, _gbs, *('a', 100, 100, 1, 0.05, 0, 0.15))
        self.assertRaises(GBS_InputException, _gbs, *('c', 0.00001, 100, 1, 0.05, 0, 0.15))
        self.assertRaises(GBS_InputException, _gbs, *('c', 100, 0.000001, 1, 0.05, 0, 0.15))
        self.assertRaises(GBS_InputException, _gbs, *('c', 100, 100, 0.0000001, 0.05, 0, 0.15))
        self.assertRaises(GBS_InputException, _gbs, *('c', 100, 100, 1, -100, 0, 0.15))
        self.assertRaises(GBS_InputException, _gbs, *('c', 100, 100, 1, 0.05, -100, 0.15))
        self.assertRaises(GBS_InputException, _gbs, *('c', 100, 100, 1, 0.05, 0, -100))
        self.assertRaises(GBS_InputException, _gbs, *('c', 100))

    # Test pricing European options and their Greeks
    def test_European_Option_Pricing(self):
        _debug("Testing European Option Pricing")
        self.assertTrue(
            assert_close(_gbs(*self.call_option_1)["value"], 4.99998980469552)
        )
        
        self.assertTrue(
            assert_close(_gbs(*self.call_option_4)["value"], 5.68695251984796) and 
            assert_close(_gbs(*self.call_option_4)["delta"], 0.50404947485) and 
            assert_close(_gbs(*self.call_option_4)["gamma"], 0.025227988795588) and 
            assert_close(_gbs(*self.call_option_4)["theta"], -2.55380111351125) and 
            assert_close(_gbs(*self.call_option_4)["vega"], 37.84198319338195) and
            assert_close(_gbs(*self.call_option_4)["rho"], 44.7179949651117)
        )
        
        self.assertTrue(
            assert_close(_gbs(*self.put_option_4)["value"], 5.68695251984796) and 
            assert_close(_gbs(*self.put_option_4)["delta"], -0.447179949651) and 
            assert_close(_gbs(*self.put_option_4)["gamma"], 0.025227988795588) and 
            assert_close(_gbs(*self.put_option_4)["theta"], -2.55380111351125) and 
            assert_close(_gbs(*self.put_option_4)["vega"], 37.84198319338195) and
            assert_close(_gbs(*self.put_option_4)["rho"], -50.4049474849597)
        )
        

if __name__ == '__main__':
    unittest.main()

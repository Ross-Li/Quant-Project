import math
from scipy.stats import norm
from scipy.stats import mvn

# Debug "switch" for more messages. Developer can toggle _DEBUG to True.
# Normally set to False
_DEBUG = False

# This class contains the limits on inputs for GBS models
# It is not intended to be part of this module's public interface
class _GBS_Limits:
    # Maximum float in this module
    MAXIMUM = 2147483248.0

    # Minimum and maximum time to expiration
    MIN_T, MAX_T = 1.0 / 1000.0, 100

    # Minimum and maximum price of underlying asset
    MIN_FS, MAX_FS = 0.01, MAXIMUM

    # Minimum and maximum strike price
    MIN_X, MAX_X = 0.01, MAXIMUM

    # Volatility smaller than 0.5% causes American Options calculations
    # to fail (Number to large errors).
    # GBS() should be OK with any positive number. Since vols less
    # than 0.5% are expected to be extremely rare, and most likely bad inputs,
    # _gbs() is assigned this limit too
    # Minimum and maximum annualized volatility
    MIN_V, MAX_V = 0.005, 1

    # Asian Option limits
    # maximum TA is time to expiration for the option
    MIN_TA = 0

    # This model will work with higher values for b, r, and V. However, such values are extremely uncommon. 
    # To catch some common errors, interest rates and volatility is capped to 100%
    # This reason for 1 (100%) is mostly to cause the library to throw exceptions 
    # if a value like 15% is entered as 15 rather than 0.15)
    # Minimum and maximum cost of carry
    MIN_b, MAX_b = -1, 1
    # Minimum and maximum risk free rate
    MIN_r, MAX_r = -1, 1

# Oh this looks like a better choice than print() for the purpose of debugging! Nice.
def _debug(debug_input):
    if (__name__ == "__main__") and (_DEBUG == True):
        print(debug_input)

class GBS_InputException(Exception):
    def __init__(self, mismatch):
        Exception.__init__(self, mismatch)

# This class defines the Exception that gets thrown when there is a calculation error
class GBS_CalculationError(Exception):
    def __init__(self, mismatch):
        Exception.__init__(self, mismatch)


# This function makes sure inputs are within limits, throws an exception otherwise
def _gbs_test_inputs(option_type, fs, x, t, r, b, v):
    if (option_type != "c") and (option_type != "p"):
        raise GBS_InputException(f"Invalid Input option_type ({option_type}). Acceptable value are: c, p")

    if (x < _GBS_Limits.MIN_X) or (x > _GBS_Limits.MAX_X):
        raise GBS_InputException(
            f"Invalid Input Strike Price (X). Acceptable range for inputs: {_GBS_Limits.MIN_X} to {_GBS_Limits.MAX_X}"
        )

    if (fs < _GBS_Limits.MIN_FS) or (fs > _GBS_Limits.MAX_FS):
        raise GBS_InputException(
            f"Invalid Input Forward/Spot Price (FS). Acceptable range for inputs: {_GBS_Limits.MIN_FS} to {_GBS_Limits.MAX_FS}"
        )

    if (t < _GBS_Limits.MIN_T) or (t > _GBS_Limits.MAX_T):
        raise GBS_InputException(
            f"Invalid Input Time (T = {t}). Acceptable range for inputs: {_GBS_Limits.MIN_T} to {_GBS_Limits.MAX_T}"
        )

    if (b < _GBS_Limits.MIN_b) or (b > _GBS_Limits.MAX_b):
        raise GBS_InputException(
            f"Invalid Input Cost of Carry (b = {b}). Acceptable range for inputs: {_GBS_Limits.MIN_b} to {_GBS_Limits.MAX_b}"
        )

    if (r < _GBS_Limits.MIN_r) or (r > _GBS_Limits.MAX_r):
        raise GBS_InputException(
            f"Invalid Input Risk Free Rate (r = {r}). Acceptable range for inputs: {_GBS_Limits.MIN_r} to {_GBS_Limits.MAX_r}"
        )

    if (v < _GBS_Limits.MIN_V) or (v > _GBS_Limits.MAX_V):
        raise GBS_InputException(
            f"Invalid Input Implied Volatility (V = {v}). Acceptable range for inputs: {_GBS_Limits.MIN_V} to {_GBS_Limits.MIN_V}"
        )

# The primary class for calculating Generalized Black Scholes option prices and deltas
# It is not intended to be part of this module's public interface

# Inputs: option_type = "p" or "c", fs = price of underlying, x = strike, t = time to expiration, r = risk free rate
#         b = cost of carry, v = implied volatility
# Outputs: value, delta, gamma, theta, vega, rho
def _gbs(option_type, fs, x, t, r, b, v):
    _debug("Debugging Information: _gbs()")

    # Test Inputs (throwing an exception on failure)
    _gbs_test_inputs(option_type, fs, x, t, r, b, v)

    # Create preliminary calculations
    t__sqrt = math.sqrt(t)
    d1 = (math.log(fs / x) + (b + (v * v) / 2) * t) / (v * t__sqrt)
    d2 = d1 - v * t__sqrt

    if option_type == "c":
        _debug("     Call Option")
        value = fs * math.exp((b - r) * t) * norm.cdf(d1) - x * math.exp(-r * t) * norm.cdf(d2)
        delta = math.exp((b - r) * t) * norm.cdf(d1)
        gamma = math.exp((b - r) * t) * norm.pdf(d1) / (fs * v * t__sqrt)
        theta = -(fs * v * math.exp((b - r) * t) * norm.pdf(d1)) / (2 * t__sqrt) - (b - r) * fs * math.exp(
            (b - r) * t) * norm.cdf(d1) - r * x * math.exp(-r * t) * norm.cdf(d2)
        vega = math.exp((b - r) * t) * fs * t__sqrt * norm.pdf(d1)
        rho = x * t * math.exp(-r * t) * norm.cdf(d2)
    else:
        _debug("     Put Option")
        value = x * math.exp(-r * t) * norm.cdf(-d2) - (fs * math.exp((b - r) * t) * norm.cdf(-d1))
        delta = -math.exp((b - r) * t) * norm.cdf(-d1)
        gamma = math.exp((b - r) * t) * norm.pdf(d1) / (fs * v * t__sqrt)
        theta = -(fs * v * math.exp((b - r) * t) * norm.pdf(d1)) / (2 * t__sqrt) + (b - r) * fs * math.exp(
            (b - r) * t) * norm.cdf(-d1) + r * x * math.exp(-r * t) * norm.cdf(-d2)
        vega = math.exp((b - r) * t) * fs * t__sqrt * norm.pdf(d1)
        rho = -x * t * math.exp(-r * t) * norm.cdf(-d2)

    _debug(f"     d1= {d1}\n     d2 = {d2}")
    _debug(f"     delta = {delta}\n     gamma = {gamma}\n     theta = {theta}\n     vega = {vega}\n     rho={rho}")
    
    return {"value": value, 
            "delta": delta, 
            "gamma": gamma, 
            "theta": theta, 
            "vega":  vega, 
            "rho":   rho}   

import math


class ErrorCalculator:
    def __init__(self, length):
        self.length = length
        self.err = {}
        self.err_num = 0
    
    def add_error_source(self, rate, name=None):
        """
        Adds an error source to use in calculations.
        Stored as a error rate
        
        Args:
            rate (double): rate that an error occurs
            name (str): (Optional) if string to have the error stored as
        """
        if name:
            self.err[name] = rate
        else:
            err_name = f"err_source{self.err_num}"
            self.err[err_name] = rate
            self.err_num += 1
    
    def add_length_dependent_error(self, err_rate_per_meter, name=None, length=None):
        """
        Adds an error source that is calculated based on the length of the link
        """
        if length is None:
            functional_len = self.length
        else:
            functional_len = length
        total_err = 1 - math.pow(1 - err_rate_per_meter, functional_len)
        self.add_error_source(total_err, name)
    
    def add_custom_error(self, error_function, *func_args, name=None, **func_kwargs):
        """
        Adds an error source calculated from a user supplied function.
        Passes the parameters *func_args and **func_kwargs to the supplied function.
        error_function cannot take name as a keyword argument
        """
        calculated_error = error_function(*func_args, **func_kwargs)
        self.add_error_source(calculated_error, name)
    
    def add_custom_length_error(self, error_function, *func_args, name=None, **func_kwargs):
        """
        Adds an error source calculated from a user supplied function.
        Passes the link length, as well as the 
        parameters *func_args and **func_kwargs to the supplied function.
        error_function cannot take name as a keyword argument
        The first parameter of error_function must be the length.
        """
        total_err = error_function(self.length, *func_args, **func_kwargs)
        self.add_error_source(total_err, name)
    
    def calculate_total_error(self):
        """
        Collects all the errors stored in the object into one total error rate.
        """
        total_rate = 1.0
        for err in self.err.values():
            total_rate *= 1 - err
        return 1 - total_rate
    
    def adjust_bitrate(self, bitrate):
        """
        Calculates the average bitrate of bits that will be received after all errors.
        
        Args:
            bitrate (double): Bitrate before errors are applied
        
        Returns:
            Adjusted average bitrate = bitrate * (1-total_errors)
        """
        total_err = self.calculate_total_error()
        return bitrate * (1 - total_err)
    
    def calculate_needed_bitrate(self, target_bitrate):
        """
        Like adjust_bitrate, but instead calculates the needed bitrate to 
        successfully transmit at target_bitrate on average
        """
        total_err = self.calculate_total_error()
        return bitrate / (1 - total_err)
        

def _test_code():
    _basic_error_test()
    _length_error_test()
    _custom_error_test()
    _custon_length_error_test()

def _basic_error_test():
    print("Testing simple errors")
    cal1 = ErrorCalculator(4)
    cal1.add_error_source(.5)
    print(f"Expected error: {.5}")
    print(f"Actual error: {cal1.calculate_total_error()}")
    cal1.add_error_source(.2)
    cal1.add_error_source(.75)
    print(f"Expected error: {.9}")
    print(f"Actual error: {cal1.calculate_total_error()}")

def _length_error_test():
    pass

# Implementation of error function for BPSK modulation, in dB
def _snr_to_bit_err(ratio):
    # convert from db to real ratio
    # snr_db = 10log(Eb/N0)
    fractional_ratio = math.pow(10,ratio/10)
    # q parameter is sqrt(2*fractional_ratio)
    q_param = math.sqrt(2*fractional_ratio)
    # probability is 
    # 1/2 * integral x->inf (e^(-t^2/2))dt
    # this simplifies to 1/2 erfc(x/sqrt(2))
    error_rate = .5 * math.erfc(q_param / math.sqrt(2))
    return error_rate

def _simple_custom_error(length):
    return 1/length

def _custom_error_test():
    pass

def _custon_length_error_test():
    print("Testing simple errors")
    cal1 = ErrorCalculator(4)
    
    cal2 = ErrorCalculator(10)
    

if __name__ == "__main__":
    _test_code()
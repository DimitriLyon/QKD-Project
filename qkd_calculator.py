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
            total_success *= 1 - err
        return 1 - total_success
    
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

def _basic_error_test():
    
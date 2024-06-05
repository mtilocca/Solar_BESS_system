import numpy as np
from scipy.signal import find_peaks, savgol_filter
from scipy.optimize import minimize

class PeakShavingAlgorithm:
    def __init__(self, consumption_data, peak_threshold, time_intervals, reduction_factor=0.9):
        """
        Initialize the PeakShavingAlgorithm class.

        :param consumption_data: List or array of power consumption data.
        :param peak_threshold: The threshold above which power consumption is considered a peak.
        :param time_intervals: List or array of corresponding time intervals.
        :param reduction_factor: The factor by which to reduce the peak consumption.
        """
        self.consumption_data = np.array(consumption_data)
        self.peak_threshold = peak_threshold
        self.time_intervals = np.array(time_intervals)
        self.reduction_factor = reduction_factor

    def smooth_data(self):
        """
        Apply Savitzky-Golay filter to smooth the data.

        :return: Smoothed power consumption data.
        """
        smoothed_data = savgol_filter(self.consumption_data, window_length=5, polyorder=2)
        return smoothed_data

    def identify_peaks(self, data):
        """
        Identify peaks in the power consumption data using scipy's find_peaks.

        :param data: Power consumption data.
        :return: Indices where peaks occur.
        """
        peaks, _ = find_peaks(data, height=self.peak_threshold)
        return peaks

    def objective_function(self, adjusted_data, peaks):
        """
        Objective function for optimization: minimize the sum of adjusted consumption data while ensuring peaks are shaved.

        :param adjusted_data: Adjusted power consumption data.
        :param peaks: Indices where peaks occur.
        :return: Objective function value.
        """
        penalty = np.sum((adjusted_data[peaks] - self.consumption_data[peaks] * self.reduction_factor) ** 2)
        return np.sum(adjusted_data) + penalty

    def shave_peaks(self):
        """
        Apply peak shaving to reduce consumption during peak periods using optimization.

        :return: Adjusted power consumption data.
        """
        smoothed_data = self.smooth_data()
        peaks = self.identify_peaks(smoothed_data)

        # Initial guess for optimization
        initial_guess = self.consumption_data.copy()

        # Constraints: Adjusted data should be less than or equal to original data at peaks
        constraints = [{'type': 'ineq', 'fun': lambda x, peak=peak: self.consumption_data[peak] * self.reduction_factor - x[peak]} for peak in peaks]

        result = minimize(self.objective_function, initial_guess, args=(peaks,), constraints=constraints, method='SLSQP')
        
        if result.success:
            return result.x
        else:
            raise ValueError("Optimization failed")

    def export_data(self):
        """
        Export the adjusted power consumption data.

        :return: Adjusted power consumption data.
        """
        return self.shave_peaks()

# # Example usage:
# consumption_data = [100, 150, 200, 300, 250, 180, 130]
# peak_threshold = 200
# time_intervals = [1, 2, 3, 4, 5, 6, 7]

# algorithm = PeakShavingAlgorithm(consumption_data, peak_threshold, time_intervals)
# adjusted_data = algorithm.export_data()
# print(adjusted_data)

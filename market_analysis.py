import arkouda as ak
import matplotlib.pyplot as plt
import numpy as np

def load_data(file_path):
    """
    Load data from a CSV file.
    """
    return ak.read_csv(file_path)

def convert_columns_to_float(data, columns):
    """
    Convert specified columns to float data type.
    """
    for column in columns:
        data[column] = ak.cast(data[column], ak.float64)
    return data

def categorize_volatility(volatility, threshold):
    """
    Categorize volatility into 'High' and 'Low' based on a threshold.
    """
    # Ensure volatility is a pdarray and the comparison results in a boolean pdarray
    condition = (volatility > threshold)

    # Use 1 for 'High' and 0 for 'Low'
    category_numerical = ak.where(condition, 1, 0)
    return category_numerical

def calculate_daily_returns(close_prices):
    """
    Calculate daily returns from closing prices.
    """
    return (close_prices[1:] - close_prices[:-1]) / close_prices[:-1]

def calculate_volatility(daily_returns, window_size=20):
    """
    Calculate rolling volatility (standard deviation) of daily returns.
    """
    volatility = ak.zeros(len(daily_returns) - window_size + 1, dtype=ak.float64)
    for i in range(len(volatility)):
        window = daily_returns[i:i+window_size]
        volatility[i] = window.std()
    return volatility

def calculate_statistics(data, column_name):
    """
    Calculate basic statistics for a given column in the dataset.
    """
    column_data = data[column_name]
    stats = {
        'mean': column_data.mean(),
        'median': column_data.median(),  
        'std_dev': column_data.std(),
        'min': column_data.min(),
        'max': column_data.max()
    }
    return stats



def find_longest_runs_and_counts(trend_array):
    """
    Find the length of the longest monotonic run and count how many of such runs exist.
    """
    trend_array_local = trend_array.to_ndarray()  # Convert to a local NumPy array
    longest_run = 0
    current_run = 0
    for value in trend_array_local:  # Now iterate over the local array
        if value:
            current_run += 1
            longest_run = max(longest_run, current_run)
        else:
            current_run = 0

    # Count the instances of the longest run
    count_longest_run = 0
    current_run = 0
    for value in trend_array_local:
        if value:
            current_run += 1
            if current_run == longest_run:
                count_longest_run += 1
                current_run = 0  # Reset to ensure each run is counted once
        else:
            current_run = 0

    return longest_run, count_longest_run


def plot_data(data, title, ylabel):
    """
    Plot the given data using Matplotlib.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(data)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel('Days')
    plt.grid(True)
    plt.show()


def analyze_volatility(volatility, daily_returns):
    """
    Analyze volatility by categorizing and performing GroupBy aggregation.
    """
    # Categorize volatility
    threshold = volatility.mean()  # Example threshold
    volatility_category = categorize_volatility(volatility, threshold)

    # Ensure that the daily_returns array is of the same length as the volatility_category array

    
    adjusted_daily_returns = daily_returns[-len(volatility_category):]

    # Group by volatility category and aggregate on daily returns
    by_volatility = ak.GroupBy(volatility_category)
    category, avg_returns = by_volatility.aggregate(adjusted_daily_returns, 'mean')

    # Print average returns by volatility category
    print("Average Returns by Volatility Category:")
    for c, r in zip(category.to_ndarray(), avg_returns.to_ndarray()):
        category_str = "High" if c == 1 else "Low"
        print(f"{category_str}: {r}")


def find_monotonic_trends(returns):
    """
    Find all instances of monotonic returns increases and decreases.
    """
    increases = ak.zeros(len(returns), dtype=ak.bool)
    decreases = ak.zeros(len(returns), dtype=ak.bool)

    for i in range(1, len(returns)):
        if returns[i] > returns[i - 1]:
            increases[i] = True
        elif returns[i] < returns[i - 1]:
            decreases[i] = True

    return increases, decreases

        

def main():
    # Connect to the Arkouda server
    ak.connect(connect_url='tcp://LARJs-MBP:5555')

    # Load data
    spx_data = load_data('SPX_500_Data.csv')

    # Convert necessary columns to float
    columns_to_convert = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    spx_data = convert_columns_to_float(spx_data, columns_to_convert)

    # Calculate daily returns
    daily_returns = calculate_daily_returns(spx_data['Close'])


    # Calculate volatility
    volatility = calculate_volatility(daily_returns)
    

    # Convert Arkouda arrays to NumPy arrays for plotting
    np_daily_returns = np.array(daily_returns.to_ndarray())
    np_volatility = np.array(volatility.to_ndarray())

    # Plot daily returns
    plot_data(np_daily_returns, 'Daily Returns', 'Returns')

    # Plot rolling volatility
    plot_data(np_volatility, 'Rolling Volatility (20-day window)', 'Volatility')

    # Calculate and print statistics for each column
    """
    for column in columns_to_convert:
        stats = calculate_statistics(spx_data, column)
        print(f"Statistics for {column}: {stats}")
    """

    # Find monotonic trends in returns
    increases, decreases = find_monotonic_trends(daily_returns)

    # Find longest run and count for increases
    longest_inc_run, count_longest_inc = find_longest_runs_and_counts(increases)

    # Find longest run and count for decreases
    longest_dec_run, count_longest_dec = find_longest_runs_and_counts(decreases)

    # Print the results for longest monotonic runs and their counts
    print("Longest Monotonic Increase Run:", longest_inc_run, "Count:", count_longest_inc)
    print("Longest Monotonic Decrease Run:", longest_dec_run, "Count:", count_longest_dec)

    # Analyze volatility
    analyze_volatility(volatility, daily_returns)

    
    # Disconnect from Arkouda server
    ak.disconnect()

if __name__ == "__main__":
    main()


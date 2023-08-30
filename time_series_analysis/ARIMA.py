import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
import sys
from sklearn.metrics import mean_absolute_error

def difference(timeseries, interval=1):
    return np.diff(timeseries, n=interval)

def fit_arima_model_with_statsmodels(train_baseline, train_data=None):
    if train_data is not None:
        model = ARIMA(train_baseline, order=(1, 1, 1), exog=train_data)
    else:
        model = ARIMA(train_baseline, order=(1, 1, 1))
    model_fit = model.fit()
    return model_fit

def inverse_difference(last_ob, forecasts):
    inverted = [forecasts[0] + last_ob]
    for i in range(1, len(forecasts)):
        inverted.append(forecasts[i] + inverted[i-1])
    return inverted

def run_arima_for_forecast_period(forecast_periods, interest_rate, perplexity_ratios=None):
    train_size = len(interest_rate) - forecast_periods
    diff_interest_rate = difference(interest_rate, interval=1)
    
    if perplexity_ratios is not None:
        diff_perplexity_ratios = difference(perplexity_ratios)
        train_baseline = diff_interest_rate[:train_size-1]
        train_data = diff_perplexity_ratios[:train_size-1]
        arima_model_statsmodels = fit_arima_model_with_statsmodels(train_baseline, train_data)
        test_data = diff_perplexity_ratios[-forecast_periods-1:-1]
        forecasts = arima_model_statsmodels.forecast(steps=forecast_periods, exog=test_data)
    else:
        train_baseline = diff_interest_rate[:train_size-1]
        arima_model_statsmodels = fit_arima_model_with_statsmodels(train_baseline)
        forecasts = arima_model_statsmodels.forecast(steps=forecast_periods)
    
    forecast_original_scale = inverse_difference(interest_rate[train_size - 2], forecasts)
    return forecast_original_scale

if len(sys.argv) < 2:
    print("Please provide the input file as a command line argument.")
    sys.exit()

input_file = sys.argv[1]
data_df = pd.read_csv(input_file, sep='\\t', header=None)
months = data_df.iloc[0, 1:].values
perplexity_ratios = data_df.iloc[2, 1:].str.replace(',', '.').astype(float).values
real_interest_rate = data_df.iloc[1, 1:].str.replace(',', '.').astype(float).values

forecast_horizons = [1, 3, 6, 9, 12]
results_with_external = []
results_without_external = []

for horizon in forecast_horizons:
    forecast_with_external = run_arima_for_forecast_period(horizon, real_interest_rate, perplexity_ratios)
    results_with_external.append(forecast_with_external)
    
    forecast_without_external = run_arima_for_forecast_period(horizon, real_interest_rate)
    results_without_external.append(forecast_without_external)

plt.figure(figsize=(18, 6))
base_variable_name = "Standardised " + data_df.iloc[1, 0].replace("_", " ")
plt.plot(months, real_interest_rate, label=base_variable_name, color='blue', linewidth=1)

colors = ['red', 'green', 'purple', 'cyan', 'orange']
labels = ['1-month forecast', '3-months forecast', '6-months forecast', '9-months forecast', '12-months forecast']

for idx, horizon in enumerate(forecast_horizons):
    forecast_months = months[len(months) - horizon - 1:len(months)]
    combined_data_with_external = [real_interest_rate[-horizon - 1]] + list(results_with_external[idx])
    plt.plot(forecast_months, combined_data_with_external, label=labels[idx], linestyle = '--', color=colors[idx], linewidth=1)
    
    combined_data_without_external = [real_interest_rate[-horizon - 1]] + list(results_without_external[idx])
    plt.plot(forecast_months, combined_data_without_external, label=f"{labels[idx]} (No Perplexities)", linestyle='-.', color=colors[idx], linewidth=1)

plt.title(f"{base_variable_name}: Original vs Forecasts")
plt.ylabel(base_variable_name)
plt.xticks(rotation=45)
plt.legend(loc="upper left")
plt.tight_layout()
plt.show()

mae_values_with_external = []
mae_values_without_external = []

for idx, horizon in enumerate(forecast_horizons):
    mae_with = mean_absolute_error(real_interest_rate[-horizon:], results_with_external[idx])
    mae_without = mean_absolute_error(real_interest_rate[-horizon:], results_without_external[idx])
    
    improvement_percentage = ((mae_without - mae_with) / mae_without) * 100
    
    mae_values_with_external.append(mae_with)
    mae_values_without_external.append(mae_without)
    print(f"Mean Absolute Error for {labels[idx]} (With External): {mae_with:.4f}")
    print(f"Mean Absolute Error for {labels[idx]} (No Perplexities): {mae_without:.4f}")
    print(f"Improvement in forecast with external variable for {labels[idx]}: {improvement_percentage:.2f}%")

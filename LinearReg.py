import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.multioutput import MultiOutputRegressor
from sklearn import datasets
import joblib

# Test Data
X, y = datasets.make_regression(n_samples=5000, n_features=5, noise=1, random_state=4)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1234)


# Real Data Import
data = pd.read.csv() # Add name of CSV File
X =  data[['w1', 'w2', 'w3']]  # Moidfy number of weights
y = data['noise_output']  # Modify header


'''
# Gradient Descent
class GradientDescent():
    def __init__(self, learnrate, iterations):
        self.lr = learnrate
        self.iter = iterations
        self.weights = None
        self.bias = None

    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0

        for _ in range(self.iter):
            y_pred = np.dot(X, self.weights) + self.bias

            dw = (2 / n_samples) * np.dot(X.T, (y_pred - y))
            db = (2 / n_samples) * np.sum(y_pred - y)

            self.weights -= self.lr * dw
            self.bias -= self.lr * db

    def prediction(self, X):
        return np.dot(X, self.weights) + self.bias
        # last iteration

    def MeanSquareError(self, y_test, prediction):
        return np.mean( (y_test - prediction) ** 2)
    
reg = GradientDescent(0.8, 10000)
reg.fit(X_train, y_train)
predictions = reg.prediction(X_test)

print('MSE: ' + str(reg.MeanSquareError(y_test, predictions)))

print('Actual values: ', y_test[:10])
print('Predicted values: ', predictions[:10])
'''



# Project Weights after Training
# Utilize imported Linear Regression Model
# Able to add bounds for weight
def apply_weight_constraints(model, lower_bounds, upper_bounds):
    # Apply constraints to each coefficient
    for i in range(len(model.coef_)):
        model.coef_[i] = np.clip(model.coef_[i], lower_bounds[i], upper_bounds[i])

# Define the bounds for the coefficients (weights)
upper_bounds = [3, 2, 5, 1, 4]
lower_bounds = [-10, 0, -5, 0, -1]

# Fit the LinearRegression model
# Wrap in multioutput regressor if necessary
reg = LinearRegression()
reg.fit(X_train, y_train)

# Apply the constraints after fitting the model
apply_weight_constraints(reg, lower_bounds, upper_bounds)

y_pred_constrained = reg.predict(X_test)
constrained_mse = np.mean((y_pred_constrained - y_test) ** 2)

print(f"Constrained Coefficients: {reg.coef_}")
print(f"Constrained MSE: {constrained_mse}")


# Data persistence
# # Store data using joblib package
# joblib.dump(reg, 'ols-model.joblib')

# # Load saved model
# loaded_model = joblib.load('ols-model.joblib')

# # Use model for prediction
# new_weights = [[1, 2, 3, 4, 5]]
# new_predict = loaded_model.predict(new_weights)
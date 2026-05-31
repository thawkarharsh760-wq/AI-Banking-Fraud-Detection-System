import pandas as pd
import sklearn

data = pd.read_csv("creditcard.csv")

print("Rows and columns:")
print(data.shape)

print("\nColumns Names:")
print(data.columns)

print("\nFirst 5 rows:")
print(data.head())

print(data['Class'].value_counts())

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

X = data.drop('Class', axis=1)
y = data['Class']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


model = LogisticRegression(max_iter=1000)

model.fit(X_train, y_train)

print("Model trained Successfully")

from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("Accuracy:", accuracy_score(y_test, predictions))

print(confusion_matrix(y_test, predictions))

print(classification_report(y_test, predictions))

from sklearn.metrics import confusion_matrix

cm = confusion_matrix(y_test, predictions)

print("Confusion Matrix:")
print(cm)

sample = X_test.iloc[0:1]

result = model.predict(sample)

if result[0] == 1:
    print("Fraud Transaction Detected")
else:
    print("Genuine Transaction")
    
    from sklearn.metrics import classification_report

print(classification_report(y_test, predictions))

import joblib

joblib.dump(model, "fraud_model.pkl")

print("Model Saved Successfully")

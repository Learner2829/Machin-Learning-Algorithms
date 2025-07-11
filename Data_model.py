import csv
import math
from collections import defaultdict
from random import shuffle

# ----------------------------------------
# Load Data
# ----------------------------------------
def load_iris_data(filename):
    data = []
    labels = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            if len(row) != 5:
                continue
            features = list(map(float, row[:4]))
            label = row[4]
            data.append(features)
            labels.append(label)
    return data, labels

# ----------------------------------------
# Add Manual Data
# ----------------------------------------
def add_manual_data(data, labels):
    while True:
        try:
            sepal_length = float(input("Enter sepal length (cm): "))
            sepal_width = float(input("Enter sepal width (cm): "))
            petal_length = float(input("Enter petal length (cm): "))
            petal_width = float(input("Enter petal width (cm): "))
            target = input("Enter target class (Iris-setosa, Iris-versicolor, Iris-virginica): ").strip()
            data.append([sepal_length, sepal_width, petal_length, petal_width])
            labels.append(target)
            print("✅ Data added successfully!")
        except ValueError:
            print("❌ Invalid input. Please enter numeric values for features.")
        
        cont = input("Do you want to add more data? (yes/no): ").strip().lower()
        if cont != 'yes':
            break

# ----------------------------------------
# Naive Bayes Core Functions
# ----------------------------------------
def group_by_class(data, labels):
    grouped = defaultdict(list)
    for x, label in zip(data, labels):
        grouped[label].append(x)
    return grouped

def summarize_class_data(grouped):
    summaries = {}
    for cls, rows in grouped.items():
        features = list(zip(*rows))  # Transpose
        summaries[cls] = [(mean(f), variance(f)) for f in features]
    return summaries

def mean(values):
    return sum(values) / len(values)

def variance(values):
    mu = mean(values)
    return sum((x - mu) ** 2 for x in values) / len(values)

def gaussian_probability(x, mu, sigma2):
    if sigma2 == 0:
        return 1 if x == mu else 0
    exponent = math.exp(-((x - mu) ** 2) / (2 * sigma2))
    return (1 / math.sqrt(2 * math.pi * sigma2)) * exponent

def predict(summaries, priors, sample):
    probabilities = {}
    for cls, feature_stats in summaries.items():
        probabilities[cls] = math.log(priors[cls])
        for i in range(len(sample)):
            mu, var = feature_stats[i]
            probabilities[cls] += math.log(gaussian_probability(sample[i], mu, var) + 1e-9)
    return max(probabilities, key=probabilities.get)

def compute_priors(grouped, total_samples):
    return {cls: len(rows) / total_samples for cls, rows in grouped.items()}

def evaluate(summaries, priors, X_test, y_test):
    correct = 0
    for x, label in zip(X_test, y_test):
        pred = predict(summaries, priors, x)
        if pred == label:
            correct += 1
    return correct / len(y_test)

# ----------------------------------------
# Manual k-Fold Cross Validation
# ----------------------------------------
def k_fold_cross_validation(data, labels, k=5):
    combined = list(zip(data, labels))
    shuffle(combined)
    fold_size = len(combined) // k
    accuracies = []

    for i in range(k):
        test_fold = combined[i * fold_size:(i + 1) * fold_size]
        train_fold = combined[:i * fold_size] + combined[(i + 1) * fold_size:]

        X_train, y_train = zip(*train_fold)
        X_test, y_test = zip(*test_fold)

        grouped = group_by_class(X_train, y_train)
        summaries = summarize_class_data(grouped)
        priors = compute_priors(grouped, len(X_train))

        acc = evaluate(summaries, priors, X_test, y_test)
        accuracies.append(acc)

    return accuracies



data, labels = load_iris_data("iris_dataset.csv")


accuracies = k_fold_cross_validation(data, labels, k=5)
print("\n🔁 5-Fold Cross-Validation Results")
for i, acc in enumerate(accuracies, 1):
    print(f" Fold {i}: {acc:.2f}")
print(f"📊 Average Accuracy: {sum(accuracies)/len(accuracies):.2f}")


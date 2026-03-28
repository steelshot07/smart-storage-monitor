import pandas as pd
import os 
import glob
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

FEATURES = [
    'smart_5_raw',
    'smart_9_raw', 
    'smart_187_raw',
    'smart_188_raw',
    'smart_190_raw',
    'smart_197_raw',
    'smart_198_raw',
]

print("Loading data...")
files = glob.glob('data/data_Q4_2025/*.csv')
dfs = [pd.read_csv(f, usecols=['failure'] + FEATURES) for f in files]
df = pd.concat(dfs, ignore_index=True)

print(f"Total rows: {len(df)}")
print(f"failures before clean: {df['failure'].sum()}")

df.dropna()
df = df[df[FEATURES].ge(0).all(axis=1)]
df[FEATURES] = df[FEATURES].clip(upper=1e9)

print(f"failures after clean: {df['failure'].sum()}")
print(f"Rows after clean: {len(df)}")

X = df[FEATURES]
y = df['failure']

X_train,X_test,y_train,y_test = train_test_split(X,y, test_size=0.2, random_state=42, stratify=y)

print("Training model...")
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight='balanced',
    n_jobs=-1,
    max_depth=10,
    min_samples_leaf=5
)

model.fit(X_train, y_train)

print("\nModel performance:")
print(classification_report(y_test, model.predict(X_test)))

importances = zip(FEATURES, model.feature_importances_)
print("\nFeature importances:")
for feature, importance in sorted(importances, key=lambda x: -x[1]):
    print(f"{feature}: {importance:.3f}")

joblib.dump(model, 'model.pkl')
joblib.dump(FEATURES, 'features.pkl')
print("\nModel saved as model.pkl and features.pkl")
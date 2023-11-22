import gzip
import pickle 
import pandas as pd

# Feature Engineering
def featureEngineering(X):
    df = pd.DataFrame(X.reset_index(drop=True))
    df['mileagePerYear'] = df['mileage']/(2021 - df['year'])
    return df

def load_data():
    with gzip.open('static/joblib_Model.gz', 'rb') as f:
        model = pickle.load(f)
    return model

def predict(data):
    model = load_data()
    df = featureEngineering(data)
    return model.predict(df)

if __name__ == "__main__":
    model = load_data()
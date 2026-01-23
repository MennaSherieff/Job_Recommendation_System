import joblib
import os
import json

def inspect():
    model_path = r"c:\Users\Zakaria\Downloads\jd\model\logistic_regression_model.pkl"
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        return

    model = joblib.load(model_path)
    print(f"Model type: {type(model)}")
    
    if hasattr(model, 'feature_names_in_'):
        features = list(model.feature_names_in_)
        print(f"Feature count: {len(features)}")
        print("Features expected by model:")
        print(json.dumps(features, indent=2))
        
        # Save to a file for the agent to read easily
        with open("model_expected_features.json", "w") as f:
            json.dump(features, f)
    else:
        print("Model does not have feature_names_in_ attribute.")

if __name__ == "__main__":
    inspect()

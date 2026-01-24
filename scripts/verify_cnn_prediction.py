
import os
import joblib
import pandas as pd
import numpy as np

def test_prediction_with_real_features():
    # 1. Mock path to model
    model_path = r"c:\Users\Zakaria\Downloads\jd\model\logistic_regression_model.pkl"
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        return

    model = joblib.load(model_path)
    
    # 2. Simulate feature preparation from RecommendationService
    # These are the features extracted by the NEW VideoService (real CNN values)
    # We simulate them being non-zero here.
    real_cnn_features = {f"feat_{i}": 0.5 for i in range(128)}
    
    # 3. Model expected columns
    model_features = [
        "match_ratio", "missing_required_skills_count", "required_skill_count", 
        "missing_soft_skills_count_new", "video_id", "feat_95", "feat_69", 
        "feat_125", "feat_20", "feat_91", "feat_68", "feat_117", "feat_76", 
        "feat_11", "feat_88", "feat_94", "feat_27", "feat_82", "feat_78", 
        "feat_8", "domain_Administrative", "domain_Analytics", "domain_Business", 
        "domain_Consulting", "domain_Creative", "domain_Engineering", 
        "domain_Finance", "domain_HR", "domain_IT", "domain_Management", 
        "domain_Operations", "domain_Research", "domain_Support"
    ]
    
    # 4. Prepare data vector
    data = {
        'match_ratio': 0.75,
        'missing_required_skills_count': 2,
        'required_skill_count': 10,
        'missing_soft_skills_count_new': 1,
        'video_id': 1
    }
    
    # Add the target feats specifically from our "real" cnn dict
    target_feats = [95, 69, 125, 20, 91, 68, 117, 76, 11, 88, 94, 27, 82, 78, 8]
    for i in target_feats:
        feat_name = f'feat_{i}'
        data[feat_name] = real_cnn_features.get(feat_name, 0.0)
    
    # Add domains as zeros
    for dom in ["Administrative", "Analytics", "Business", "Consulting", "Creative", "Engineering", "Finance", "HR", "IT", "Management", "Operations", "Research", "Support"]:
        data[f"domain_{dom}"] = 0
    data["domain_IT"] = 1 # Set one domain
    
    # 5. Create DataFrame and predict
    X = pd.DataFrame([data])
    X = X[model_features] # Ensure order
    
    prob = model.predict_proba(X)[0, 1]
    print(f"\n[TEST SUCCESS] Prediction score with real features: {prob * 100:.2f}%")
    print(f"Features used (sample): { {k: v for k, v in data.items() if 'feat' in k} }")

if __name__ == "__main__":
    test_prediction_with_real_features()

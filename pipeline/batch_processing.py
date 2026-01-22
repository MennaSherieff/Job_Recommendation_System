import pandas as pd
import numpy as np

def create_cv_jd_matching_dataframe(
    cv_df: pd.DataFrame,
    jd_df: pd.DataFrame,
    cv_id_col: str = 'cv_id',
    jd_id_col: str = 'jd_id',
    cv_hard_vec_col: str = 'hard_vector',
    cv_soft_vec_col: str = 'soft_vector',
    jd_hard_vec_col: str = 'hard_vector',
    jd_soft_vec_col: str = 'soft_vector',
    jd_hard_skills_col: str = 'required_hard_skills',
    jd_soft_skills_col: str = 'required_soft_skills'
) -> pd.DataFrame:
    """
    Create pairwise CV-JD matching features for all combinations.
    
    Args:
        cv_df: DataFrame with CV features (must include skill vectors)
        jd_df: DataFrame with JD features (must include skill vectors)
        cv_id_col: Column name for CV identifier
        jd_id_col: Column name for JD identifier
        cv_hard_vec_col: Column name for CV hard skill vector
        cv_soft_vec_col: Column name for CV soft skill vector
        jd_hard_vec_col: Column name for JD hard skill vector
        jd_soft_vec_col: Column name for JD soft skill vector
        jd_hard_skills_col: Column name for JD required hard skills
        jd_soft_skills_col: Column name for JD required soft skills
        
    Returns:
        DataFrame with one row per CV-JD pair containing matching features
    """
    rows = []
    
    for _, cv in cv_df.iterrows():
        for _, jd in jd_df.iterrows():
            mw, rw, mr, miss_count, miss_hard, miss_soft = compute_match_features(
                cv[cv_hard_vec_col],
                jd[jd_hard_vec_col],
                cv[cv_soft_vec_col],
                jd[jd_soft_vec_col]
            )
            
            rows.append({
                "cv_id": cv[cv_id_col],
                "jd_id": jd[jd_id_col],
                "matched_weight": mw,
                "required_weight": rw,
                "match_ratio": mr,
                "missing_required_skills_count": miss_count,
                "missing_hard_skills": miss_hard,
                "missing_soft_skills": miss_soft,
                "required_hard_skills": jd[jd_hard_skills_col],
                "required_soft_skills": jd[jd_soft_skills_col],
                "required_skill_count": len(jd[jd_hard_skills_col]) + len(jd[jd_soft_skills_col])
            })
    
    return pd.DataFrame(rows)

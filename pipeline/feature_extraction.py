import re
from typing import List, Dict, Tuple, Optional, Union
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


# ============================================================================
# SKILL DICTIONARIES
# ============================================================================

HARD_SKILLS_DICT = {
    # Programming & Development
    "python": ["python"],
    "software development": ["software", "software development"],
    "backend development": ["backend", "backend development"],
    "web development": ["web", "web development"],
    "cloud computing": ["cloud"],
    "automation": ["automation"],
    "testing": ["testing"],
    "frameworks": ["frameworks"],
    "code": ["code", "coding"],

    # Data & AI
    "data analysis": ["data analysis", "analysis"],
    "data science": ["data science"],
    "machine learning": ["machine learning", "machine"],
    "ai": ["ai", "artificial intelligence"],
    "models": ["models", "model"],
    "reporting": ["reporting", "reports"],

    # Engineering
    "engineering": ["engineering"],
    "systems engineering": ["systems", "system"],
    "networking": ["network", "networking"],

    # Business & Finance
    "financial analysis": ["financial", "finance"],
    "accounting": ["accounting"],
    "sales": ["sales"],
    "marketing": ["marketing", "digital marketing"],
    "product management": ["product"],
    "operations management": ["operations"],
    "project management": ["project", "projects"],

    # Tools & Platforms
    "microsoft office": ["microsoft", "office"],
    "crm systems": ["crm"],
    "software tools": ["tools"],
    "applications": ["applications"],
    "technology platforms": ["technology", "technologies"],

    # HR & Recruitment
    "recruitment": ["recruitment", "hiring", "talent acquisition"],
    "human resources": ["employee", "candidates", "candidate"]
}

SOFT_SKILLS_DICT = {
    "communication": ["communication"],
    "teamwork": ["team", "teams", "collaborate", "collaboration"],
    "problem solving": ["problem", "issues", "solutions"],
    "leadership": ["lead", "manager", "management"],
    "time management": ["time", "timely"],
    "customer focus": ["customer", "customers", "client", "clients", "service"],
    "adaptability": ["learning", "innovation"],
    "attention to detail": ["quality", "standards", "compliance"],
    "organizational skills": ["organization", "process", "processes"],
    "analytical thinking": ["analysis", "identify", "understanding"],
    "work ethic": ["responsible", "accountable"],
    "collaboration": ["across", "internal", "external"],
    "growth mindset": ["growth", "improve", "develop"]
}

# Master skill lists - ordered consistently
MASTER_HARD_SKILLS = list(HARD_SKILLS_DICT.keys())
MASTER_SOFT_SKILLS = list(SOFT_SKILLS_DICT.keys())


# ============================================================================
# TEXT PREPROCESSING
# ============================================================================

def clean_text(text: Union[str, float, None]) -> str:
    """
    Clean and preprocess text for skill extraction.
    
    Steps:
    1. Handle missing/invalid values
    2. Convert to lowercase
    3. Remove special characters (keep letters, numbers, basic punctuation)
    4. Remove URLs
    5. Remove mentions (@username)
    6. Remove boilerplate phrases
    7. Tokenize
    8. Remove stopwords
    9. Lemmatize tokens
    
    Args:
        text: Input text to clean. Can be str, float (NaN), or None.
        
    Returns:
        Cleaned text as a single string with tokens separated by spaces.
        
    Examples:
        >>> clean_text("The developer has 5+ years of Python experience.")
        "developer year python experience"
    """
    # Handle missing or non-string values
    if not isinstance(text, str):
        return ""
    
    # Normalize to lowercase
    text = text.lower()
    
    # Remove special characters, keep letters, numbers, and basic punctuation
    pat = r'[^a-zA-Z.,!?/:;\"\'\s]'
    text = re.sub(pat, ' ', text)
    
    # Remove URLs
    text = re.sub(r'https?:\S*', '', text)
    
    # Remove mentions
    text = re.sub(r'@\S*', '', text)
    
    # Remove boilerplate/irrelevant phrases (case-insensitive via lowercase above)
    boilerplate_pattern = (
        r'\b(view on map|additional information|job number|marriott|'
        r'jw marriott|le ridien|equal opportunity|employee happy|join portfolio)\b'
    )
    text = re.sub(boilerplate_pattern, '', text)
    
    # Tokenize by whitespace
    tokens = text.split()
    
    # Load stopwords and lemmatizer (stateless within function)
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    
    # Remove stopwords and lemmatize
    cleaned_tokens = [
        lemmatizer.lemmatize(word) 
        for word in tokens 
        if word not in stop_words
    ]
    
    return " ".join(cleaned_tokens)


# ============================================================================
# SKILL EXTRACTION
# ============================================================================

def extract_skills_from_text(
    text: str, 
    skill_dict: Dict[str, List[str]]
) -> List[str]:
    """
    Extract skills from text using exact lexicon matching.
    
    For each canonical skill, checks if any of its variants appear in the text.
    Each skill is extracted at most once (presence-based, not frequency-based).
    
    Args:
        text: Cleaned text to search for skills (should be preprocessed/lowercased)
        skill_dict: Dictionary mapping canonical skill names to variant lists
        
    Returns:
        List of canonical skill names found in the text
        
    Examples:
        >>> text = "python machine learning team collaboration"
        >>> extract_skills_from_text(text, HARD_SKILLS_DICT)
        ['python', 'machine learning']
    """
    found_skills = []
    
    for canonical_skill, variants in skill_dict.items():
        for variant in variants:
            if variant in text:
                found_skills.append(canonical_skill)
                break  # Only add each canonical skill once
    
    return found_skills


def vectorize_skills(
    skill_list: List[str], 
    master_skills: List[str]
) -> List[int]:
    """
    Convert a list of skills into a binary vector aligned with master skill list.
    
    Args:
        skill_list: List of skills present (canonical names)
        master_skills: Ordered list of all possible skills (defines vector dimension)
        
    Returns:
        Binary vector where 1 indicates skill presence, 0 indicates absence
        
    Examples:
        >>> vectorize_skills(['python', 'ai'], MASTER_HARD_SKILLS)
        [1, 0, 0, ..., 1, ...]  # length = len(MASTER_HARD_SKILLS)
    """
    return [1 if skill in skill_list else 0 for skill in master_skills]


# ============================================================================
# CV-JD MATCHING
# ============================================================================

def compute_match_features(
    cv_hard_vec: List[int],
    jd_hard_vec: List[int],
    cv_soft_vec: List[int],
    jd_soft_vec: List[int]
) -> Tuple[int, int, float, int, List[str], List[str]]:
    """
    Compute matching features between a CV and a job description.
    
    Calculates skill alignment metrics based on binary skill vectors.
    
    Args:
        cv_hard_vec: Binary vector of hard skills in CV
        jd_hard_vec: Binary vector of hard skills required by job
        cv_soft_vec: Binary vector of soft skills in CV
        jd_soft_vec: Binary vector of soft skills required by job
        
    Returns:
        Tuple containing:
        - matched_weight: Number of required hard skills present in CV
        - required_weight: Total number of hard skills required by job
        - match_ratio: Proportion of required hard skills matched (0-1)
        - missing_required_skills_count: Number of required hard skills missing
        - missing_hard_skills: List of missing required hard skill names
        - missing_soft_skills: List of missing required soft skill names
        
    Examples:
        >>> cv_hard = [1, 0, 1, 0]
        >>> jd_hard = [1, 1, 0, 0]
        >>> cv_soft = [1, 1]
        >>> jd_soft = [1, 0]
        >>> compute_match_features(cv_hard, jd_hard, cv_soft, jd_soft)
        (1, 2, 0.5, 1, ['software development'], [])
    """
    # Count matched required hard skills
    matched_weight = sum(
        1 for i in range(len(cv_hard_vec)) 
        if cv_hard_vec[i] and jd_hard_vec[i]
    )
    
    # Count total required hard skills
    required_weight = sum(jd_hard_vec)
    
    # Calculate match ratio (handle division by zero)
    match_ratio = matched_weight / required_weight if required_weight > 0 else 0.0
    
    # Count missing required hard skills
    missing_required_skills_count = sum(
        1 for i in range(len(jd_hard_vec)) 
        if jd_hard_vec[i] and not cv_hard_vec[i]
    )
    
    # Identify missing hard skills by name
    missing_hard_skills = [
        MASTER_HARD_SKILLS[i] 
        for i in range(len(jd_hard_vec)) 
        if jd_hard_vec[i] and not cv_hard_vec[i]
    ]
    
    # Identify missing soft skills by name
    missing_soft_skills = [
        MASTER_SOFT_SKILLS[i] 
        for i in range(len(jd_soft_vec)) 
        if jd_soft_vec[i] and not cv_soft_vec[i]
    ]
    
    return (
        matched_weight,
        required_weight,
        match_ratio,
        missing_required_skills_count,
        missing_hard_skills,
        missing_soft_skills
    )


# ============================================================================
# HIGH-LEVEL FEATURE EXTRACTION FUNCTIONS
# ============================================================================

def extract_cv_features(cv_text: str) -> Dict[str, Union[str, List[str], List[int]]]:
    """
    Extract all features from a CV text.
    
    Performs cleaning, skill extraction, and vectorization in one pass.
    
    Args:
        cv_text: Raw CV text
        
    Returns:
        Dictionary containing:
        - clean_text: Preprocessed text
        - hard_skills: List of extracted hard skill names
        - soft_skills: List of extracted soft skill names
        - hard_vector: Binary vector of hard skills
        - soft_vector: Binary vector of soft skills
    """
    clean = clean_text(cv_text)
    
    hard_skills = extract_skills_from_text(clean, HARD_SKILLS_DICT)
    soft_skills = extract_skills_from_text(clean, SOFT_SKILLS_DICT)
    
    hard_vector = vectorize_skills(hard_skills, MASTER_HARD_SKILLS)
    soft_vector = vectorize_skills(soft_skills, MASTER_SOFT_SKILLS)
    
    return {
        "clean_text": clean,
        "hard_skills": hard_skills,
        "soft_skills": soft_skills,
        "hard_vector": hard_vector,
        "soft_vector": soft_vector
    }


def extract_jd_features(jd_text: str) -> Dict[str, Union[str, List[str], List[int], int]]:
    """
    Extract all features from a job description text.
    
    Performs cleaning, skill extraction, and vectorization in one pass.
    
    Args:
        jd_text: Raw job description text
        
    Returns:
        Dictionary containing:
        - clean_text: Preprocessed text
        - required_hard_skills: List of required hard skill names
        - required_soft_skills: List of required soft skill names
        - hard_vector: Binary vector of required hard skills
        - soft_vector: Binary vector of required soft skills
        - skill_count: Total number of required skills
    """
    clean = clean_text(jd_text)
    
    hard_skills = extract_skills_from_text(clean, HARD_SKILLS_DICT)
    soft_skills = extract_skills_from_text(clean, SOFT_SKILLS_DICT)
    
    hard_vector = vectorize_skills(hard_skills, MASTER_HARD_SKILLS)
    soft_vector = vectorize_skills(soft_skills, MASTER_SOFT_SKILLS)
    
    return {
        "clean_text": clean,
        "required_hard_skills": hard_skills,
        "required_soft_skills": soft_skills,
        "hard_vector": hard_vector,
        "soft_vector": soft_vector,
        "skill_count": len(hard_skills) + len(soft_skills)
    }


def compute_cv_jd_match(
    cv_features: Dict[str, Union[str, List[str], List[int]]],
    jd_features: Dict[str, Union[str, List[str], List[int], int]]
) -> Dict[str, Union[int, float, List[str]]]:
    """
    Compute matching features between a CV and a job description.
    
    Args:
        cv_features: Output from extract_cv_features()
        jd_features: Output from extract_jd_features()
        
    Returns:
        Dictionary containing:
        - matched_weight: Number of required hard skills matched
        - required_weight: Total required hard skills
        - match_ratio: Proportion of required skills matched
        - missing_required_skills_count: Count of missing required hard skills
        - missing_hard_skills: List of missing hard skill names
        - missing_soft_skills: List of missing soft skill names
        - required_hard_skills: List of required hard skills
        - required_soft_skills: List of required soft skills
        - required_skill_count: Total required skills
    """
    mw, rw, mr, miss_count, miss_hard, miss_soft = compute_match_features(
        cv_features["hard_vector"],
        jd_features["hard_vector"],
        cv_features["soft_vector"],
        jd_features["soft_vector"]
    )
    
    return {
        "matched_weight": mw,
        "required_weight": rw,
        "match_ratio": mr,
        "missing_required_skills_count": miss_count,
        "missing_hard_skills": miss_hard,
        "missing_soft_skills": miss_soft,
        "required_hard_skills": jd_features["required_hard_skills"],
        "required_soft_skills": jd_features["required_soft_skills"],
        "required_skill_count": jd_features["skill_count"]
    }


# ============================================================================
# BATCH PROCESSING FUNCTIONS
# ============================================================================

def process_job_descriptions_dataframe(
    df: pd.DataFrame,
    summary_col: str = 'summary',
    responsibilities_col: str = 'responsibilities',
    qualifications_col: str = 'qualifications'
) -> pd.DataFrame:
    """
    Process a dataframe of job descriptions to extract skills and features.
    
    Args:
        df: DataFrame with job description columns
        summary_col: Column name for job summary
        responsibilities_col: Column name for responsibilities
        qualifications_col: Column name for qualifications
        
    Returns:
        DataFrame with additional columns:
        - summary_cleaned
        - responsibilities_cleaned
        - qualifications_cleaned
        - job_description_clean (concatenated)
        - required_hard_skills
        - required_soft_skills
        - skill_count
    """
    df = df.copy()
    
    # Fill NaN values
    text_cols = [summary_col, responsibilities_col, qualifications_col]
    df[text_cols] = df[text_cols].fillna("")
    
    # Clean individual columns
    df['summary_cleaned'] = df[summary_col].apply(clean_text)
    df['responsibilities_cleaned'] = df[responsibilities_col].apply(clean_text)
    df['qualifications_cleaned'] = df[qualifications_col].apply(clean_text)
    
    # Concatenate cleaned text
    df['job_description_clean'] = (
        df['summary_cleaned'] + " " +
        df['responsibilities_cleaned'] + " " +
        df['qualifications_cleaned']
    )
    
    # Extract skills
    df['required_hard_skills'] = df['job_description_clean'].apply(
        lambda x: extract_skills_from_text(x, HARD_SKILLS_DICT)
    )
    
    df['required_soft_skills'] = df['job_description_clean'].apply(
        lambda x: extract_skills_from_text(x, SOFT_SKILLS_DICT)
    )
    
    # Calculate skill count
    df['skill_count'] = (
        df['required_hard_skills'].apply(len) +
        df['required_soft_skills'].apply(len)
    )
    
    return df


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_master_skills() -> Tuple[List[str], List[str]]:
    """
    Get the master skill lists used for vectorization.
    
    Returns:
        Tuple of (MASTER_HARD_SKILLS, MASTER_SOFT_SKILLS)
    """
    return MASTER_HARD_SKILLS.copy(), MASTER_SOFT_SKILLS.copy()


def get_skill_dictionaries() -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """
    Get the skill dictionaries used for extraction.
    
    Returns:
        Tuple of (HARD_SKILLS_DICT, SOFT_SKILLS_DICT)
    """
    return HARD_SKILLS_DICT.copy(), SOFT_SKILLS_DICT.copy()
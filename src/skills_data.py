"""
skills_data.py
--------------
This file holds our "known skills" database.

Why a dictionary of aliases?
Real resumes and job descriptions don't always use the same wording for the
same skill. For example, someone might write "JS", "Javascript", or
"JavaScript" - these all mean the same thing. Instead of hardcoding these
special cases into our extraction logic, we keep a simple mapping here:

    canonical_skill_name -> [list of alternate spellings / abbreviations]

This makes the project easy to extend: to teach the app a new skill, you
just add one line here. No other code needs to change.
"""

# Each key is the "canonical" (standard) name we will display to the user.
# Each value is a list of alternate ways that skill might appear in text.
# The canonical name itself is always treated as a valid alias too.
SKILL_ALIASES = {
    # Programming Languages
    "Python": ["python", "py"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js", "es6", "ecmascript"],
    "TypeScript": ["typescript", "ts"],
    "C++": ["c++", "cpp"],
    "C": ["c programming"],
    "C#": ["c#", "csharp"],
    "SQL": ["sql", "structured query language"],
    "R": ["r programming", "r language"],
    "Go": ["golang", "go lang"],
    "PHP": ["php"],
    "Ruby": ["ruby"],
    "Kotlin": ["kotlin"],
    "Swift": ["swift"],

    # Web Development
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "React": ["react", "react.js", "reactjs"],
    "Angular": ["angular", "angular.js", "angularjs"],
    "Vue.js": ["vue", "vue.js", "vuejs"],
    "Node.js": ["node", "node.js", "nodejs"],
    "Express.js": ["express", "express.js", "expressjs"],
    "Django": ["django"],
    "Flask": ["flask"],
    "Streamlit": ["streamlit"],
    "FastAPI": ["fastapi", "fast api"],
    "Bootstrap": ["bootstrap"],
    "REST API": ["rest api", "restful api", "rest apis"],

    # Data Science / ML / NLP
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning", "dl"],
    "Natural Language Processing": ["nlp", "natural language processing"],
    "Computer Vision": ["computer vision", "cv"],
    "TensorFlow": ["tensorflow", "tf"],
    "PyTorch": ["pytorch", "torch"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "Keras": ["keras"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Matplotlib": ["matplotlib"],
    "Seaborn": ["seaborn"],
    "Plotly": ["plotly"],
    "spaCy": ["spacy"],
    "NLTK": ["nltk"],
    "OpenCV": ["opencv", "open cv", "cv2"],
    "Data Analysis": ["data analysis", "data analytics"],
    "Data Visualization": ["data visualization", "data viz"],
    "Statistics": ["statistics", "statistical analysis"],
    "TF-IDF": ["tf-idf", "tfidf"],

    # Databases
    "MySQL": ["mysql"],
    "PostgreSQL": ["postgresql", "postgres"],
    "MongoDB": ["mongodb", "mongo"],
    "SQLite": ["sqlite"],
    "Redis": ["redis"],
    "Firebase": ["firebase"],
    "Oracle": ["oracle database", "oracle db"],

    # Cloud & DevOps
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure", "microsoft azure"],
    "Google Cloud Platform": ["gcp", "google cloud", "google cloud platform"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "Git": ["git"],
    "GitHub": ["github"],
    "GitLab": ["gitlab"],
    "CI/CD": ["ci/cd", "ci cd", "continuous integration"],
    "Linux": ["linux", "unix"],
    "Jenkins": ["jenkins"],

    # Tools / Other
    "Excel": ["excel", "ms excel", "microsoft excel"],
    "Tableau": ["tableau"],
    "Power BI": ["power bi", "powerbi"],
    "Jupyter": ["jupyter", "jupyter notebook"],
    "VS Code": ["vs code", "visual studio code", "vscode"],
    "Postman": ["postman"],
    "Agile": ["agile", "agile methodology", "scrum"],
    "Regex": ["regex", "regular expressions"],
    "OOP": ["oop", "object-oriented programming", "object oriented programming"],
    "Data Structures": ["data structures", "dsa"],
    "Algorithms": ["algorithms"],
}


def build_alias_lookup():
    """
    Build a reverse lookup dictionary: alias_text -> canonical_name.

    This lets us take any raw text found in a resume (e.g. "reactjs") and
    quickly find out which canonical skill it belongs to (e.g. "React").

    We store alias text in lowercase since matching will be case-insensitive.
    """
    lookup = {}
    for canonical, aliases in SKILL_ALIASES.items():
        # Always include the canonical name itself as a valid alias
        all_forms = set(aliases) | {canonical.lower()}
        for alias in all_forms:
            lookup[alias.lower()] = canonical
    return lookup

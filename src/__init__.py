"""
Resume Analyzer core package.

This package holds all the "business logic" of the app - PDF extraction,
text preprocessing, skill extraction, similarity scoring, and final
score calculation. Keeping this logic separate from app.py (the Streamlit
UI) makes the project modular: each piece can be tested and understood
on its own, and app.py just wires them together.
"""

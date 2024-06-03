# GitHub steps

# Initialize Git repository
git init

# Create .gitignore file
echo "__pycache__/
*.pyc
*.pyo
venv/
env/
.DS_Store
*.sqlite3
*.log
*.db" > .gitignore

# Add files to Git
git add .

# Commit files
git commit -m "Initial commit"

# Link to GitHub repository
git remote add origin https://github.com/your-username/fastapi-genai.git
git branch -M main
git push -u origin main

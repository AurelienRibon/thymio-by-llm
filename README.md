# Thymio by LLM

## How can I run this?

Currently, the simplest way is to clone this repository and run the `main.py` file.

1. Ensure you have an openai API key in your environment variables.

```bash
# Put this in your .bashrc or .zshrc, to avoid having to do it every time
export OPENAI_API_KEY="your-api-key"
```

2. Be sure to open the Thymio Suite before running the script.

3. Run the script.

```bash
# Clone the repository
git clone https://github.com/AurelienRibon/thymio-by-llm.git
cd thymio-by-llm

# (optional) Create a virtual environment
pip3 -m venv .venv
source .venv/bin/activate

# Install the required packages
pip3 install -r requirements.txt

# Run the main file
python3 src/main.py
```

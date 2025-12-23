# Delta V

Delta V is a market volatility and sentiment analysis tool. The idea is to generate recommendation on specific swing trading plays based on meticulous curated technical data.

**Context:** Volatility hunter and sentiment analysis dashboard.
**Runtime:** Python 3.10+ (Streamlit).

### Prerequisites

* **Python:** Version 3.10 or higher.
* **Virtual Environment:** Strictly required to isolate dependencies.



### Dev environment setup


1. Configure environment
* Create a `.env` file from `.envtemplate`.
* Add your gemini API key.

2. Build and deploy 
```bash
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# deploy dashboard
streamlit run dashboard.py

```


# AI Usage

All AIs refers to AI_RULES.md
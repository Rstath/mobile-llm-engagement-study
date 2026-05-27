# Human + Engagement Agent Experiment App v3

This version uses Streamlit multipage structure:

- `app.py`: Researcher/Admin page
- `pages/01_Participant.py`: Participant-only mobile chat page

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
python -m streamlit run app.py
```

Then Streamlit will show pages in the sidebar.

For participant testing, open:

```text
http://localhost:8501/Participant
```

or select **Participant** from the Streamlit pages menu.

## Configure OpenAI

Create `.env`:

```text
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

## Important

The participant page hides researcher information and displays only the mobile-style conversation.
The user writes messages inside the mobile-style interface.

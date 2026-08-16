from agents.triage_agent import triage_agent

state = {
    "english_text": "I have chest pain and difficulty breathing."
}

result = triage_agent(state)

print(result)
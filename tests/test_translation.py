from agents.translation_node import translation_node

state = {
    "spoken_text": "मुझे सीने में दर्द है और सांस लेने में तकलीफ हो रही है"
}

result = translation_node(state)

print(result)
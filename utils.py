def format_message(username, message):
    return f"{username}: {message}"

def save_chat_history(history, filename='chat_history.txt'):
    with open(filename, 'a') as f:
        for entry in history:
            f.write(f"{entry}\n")

def load_chat_history(filename='chat_history.txt'):
    try:
        with open(filename, 'r') as f:
            return f.readlines()
    except FileNotFoundError:
        return []
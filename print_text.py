# We'll use RGB values: R: 0, G: 255, B: 0
BRIGHT_GREEN = '\033[38;2;0;255;1m'
BRIGHT_ORANGE = '\033[38;2;255;128;0m'

# Reset code
RESET = '\033[0m'

# # Print text in bright green
# print(BRIGHT_GREEN + "This is bright green text!" + RESET)

# # Print text in bright orange
# print(BRIGHT_ORANGE + "This is bright orange text!" + RESET)

def print_text(text, color="o"):
    if color == "g":
        print(BRIGHT_GREEN + text + RESET)
    else:
        print(BRIGHT_ORANGE + text + RESET)
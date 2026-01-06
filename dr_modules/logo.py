# color_luffy.py
from colorama import init, Fore, Style
import time
import os
import sys

# Initialize colorama (works on Windows too)
init(autoreset=True)

logo = r'''
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣤⠶⠶⠶⠶⠤⠤⠤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠔⠊⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠛⠷⣦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⢶⣾⠋⢉⣉⣉⣛⣛⣍⣽⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠷⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⠴⠋⢀⡔⠉⠀⠀⣀⣠⣤⣤⣵⣼⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⣴⣏⡥⠔⠊⠉⣀⣤⠞⠉⠀⠀⠀⠀⠀⠈⡇⣨⠆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⠿⠟⠛⠛⢿⣶⡶⣦⣤⣄⣀⠀⠀⠀⠀
    ⠀⠀⢀⠶⠒⠋⣹⠟⢉⣀⠤⠖⠛⠉⠀⢀⣠⠴⠚⠉⠉⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢶⣦⡀⠀⠀⠀⠉⠁⠀⠀⠀⠉⠙⠻⣶⣄⠀
    ⠀⡴⠿⠒⠒⡾⠀⢠⠾⠁⠀⣀⡀⠀⣴⡋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠈⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣇
    ⠘⠇⠀⢀⡞⠀⠀⠀⠀⢠⡾⠋⠀⠀⠈⠉⠉⠉⠉⠉⠉⠉⠉⠉⠻⠉⣻⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣹⣿⣿⡭⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡏
    ⠀⠀⢠⠞⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⣀⣠⣤⠤⠤⠤⠤⠤⠤⠤⠔⠚⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣾⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡿⠁
    ⠀⣰⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⣿⣶⣿⣧⣾⣤⣀⣀⣀⣰⡄⠀⢀⣀⣶⣤⣤⣾⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⡟⠁⠀
    ⠐⠋⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⣀⠀⣀⣴⠟⠋⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⣿⠟⠋⠉⠉⠛⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⣀⣼⠿⠋⠁⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⡿⠁⠀⠀⠀⠀⠀⠀⠈⠋⠙⠛⠛⠛⠛⠛⠛⠛⠛⠛⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⢀⣠⣤⣶⡟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⣀⣴⠾⣏⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⣿⣿⣿⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⣠⠴⠋⠁⠀⠀⣿⣿⣦⣀⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣤⣶⣿⣿⣿⣿⣿⣿⣿⡿⢿⣆⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⡼⠃⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣶⣤⣤⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⣴⣾⠟⠉⣿⣿⣿⣿⣿⣿⣿⡿⠿⣿⣧⠀⠻⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠜⠁⠀⠀⠀⠀⠀⢸⡏⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣿⣶⣿⣿⣿⣿⣿⣿⣿⣏⡁⠉⠋⢁⣠⡾⠿⠛⣿⣿⡇⢹⣿⣿⣶⣌⠙⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠛⠻⢿⣯⡉⠉⠉⣅⣰⣶⠂⢠⣿⡟⢀⣾⣿⣆⠀⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠻⠈⢿⣿⣿⣿⣏⠉⠉⠉⠉⠉⠉⢹⣿⣇⠀⠀⠀⠀⠀⠈⠀⠐⠋⠓⠀⠀⣼⣋⣴⡇⠀⠈⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠿⣧⡉⠀⠀⠀⠀⠀⠀⠘⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⠋⠛⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣄⠀⠀⠀⠀⠀⠀⠙⠛⠃⠀⠀⠀⠀⠀⠀⠀⠀⢀⠜⠉⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⠿⣷⣄⠀⠀⠐⠒⠒⠒⠒⠒⠒⠒⠒⠀⠀⠀⣠⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⠘⣷⣤⡀⠀⠀⠘⠛⠛⠂⠀⠀⠀⣠⡾⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠘⣿⣿⣷⣦⣄⡀⠀⠀⣀⣴⣿⣿⠰⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⠀⣀⡘⠀⠀⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⢻⡀⠀⢀⣀⣀⣠⣤⣤⣄⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⢀⡾⠋⠉⠁⠀⠀⠈⠉⠉⢹⠇⠀⠀⠀⢹⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠘⢿⡛⠉⠉⠁⠀⠀⠀⠀⠀⠉⠙⢿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⢠⣾⠀⠀⠀⠀⣀⣤⣴⣶⠾⠏⠀⠀⢣⠀⠀⢻⣿⣿⣿⡿⠋⢹⣿⠇⠀⠀⠀⠀⠙⢆⣀⣤⣤⣄⣀⡀⠀⠀⠀⠀⠙⢷⡄⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠉⠀⠀⠀⢀⡾⠛⠛⠻⣏⠀⠀⠀⠀⢸⣇⠀⠀⢿⣿⡛⠁⠀⣾⡿⠀⣠⠀⠀⠀⠀⠀⠙⣿⣿⣿⣿⣿⣷⡄⠀⠀⠀⠀⠙⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠁⠀⠀⠀⢹⣆⠀⠀⠀⢸⣿⡄⠀⠈⣿⡇⠀⢠⣿⠇⢰⡏⠀⠀⠀⠀⠀⣰⠇⠀⠀⠉⠉⠛⢿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

    
'''

# Choose color palette (colorama Fore constants)
# PALETTE = [
#     Fore.RED + Style.BRIGHT,
#     Fore.YELLOW + Style.BRIGHT,
#     Fore.GREEN + Style.BRIGHT,
#     Fore.CYAN + Style.BRIGHT,
#     Fore.BLUE + Style.BRIGHT,
#     Fore.MAGENTA + Style.BRIGHT
# ]

PALETTE = [Fore.MAGENTA + Style.BRIGHT, Fore.BLUE]



# Modes: "line" (one color per line) or "char" (rainbow per character)
MODE = "char"   # change to "line" for line-based coloring
ANIMATE = False  # set True to animate (cycles frames) - may flicker in some terminals
SLEEP_BETWEEN_FRAMES = 0.08  # only used if ANIMATE = True
FRAMES = 8  # number of frames in animation cycle

def colored_by_line(text):
    out_lines = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        color = PALETTE[i % len(PALETTE)]
        out_lines.append(color + line + Style.RESET_ALL)
    return "\n".join(out_lines)

def colored_by_char(text, phase=0):
    out_lines = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        colored_chars = []
        for j, ch in enumerate(line):
            # pick color based on character index plus a phase for animation
            idx = (i + j + phase) % len(PALETTE)
            colored_chars.append(PALETTE[idx] + ch)
        out_lines.append("".join(colored_chars) + Style.RESET_ALL)
    return "\n".join(out_lines)

def clear():
    # cross-platform clear
    os.system('cls' if os.name == 'nt' else 'clear')

def interface():
    try:
        if not ANIMATE:
            if MODE == "line":
                print(colored_by_line(logo))
            else:
                print(colored_by_char(logo, phase=0))
        else:
            # animated rainbow cycle
            frame = 0
            while True:
                clear()
                if MODE == "line":
                    print(colored_by_line(logo))
                else:
                    print(colored_by_char(logo, phase=frame))
                frame = (frame + 1) % FRAMES
                time.sleep(SLEEP_BETWEEN_FRAMES)
    except KeyboardInterrupt:
        # Restore terminal colors nicely
        print(Style.RESET_ALL)
        sys.exit(0)


    # realistic professional banner (DarkReaper - OSINT tool)
    from colorama import Fore, Style, init
    init(autoreset=True)

    print(Fore.CYAN + "="*68)
    print(Fore.RED + " " * 28 + "DarkReaper")
    print(Fore.CYAN + " " * 11 + "Automated Intelligence Gathering Tool (OSINT)")
    print(Fore.WHITE + " " * 28 + "Developed by " + Fore.GREEN + "Viraj Kadam")
    print(Fore.CYAN + " " * 24 + "Final Year BE Project - 2025")
    print(Fore.CYAN + "="*68)

    print(Fore.YELLOW + "\n[+] Project Title : " + Fore.WHITE + "Automated Intelligence Gathering Tool (OSINT)")
    # print(Fore.YELLOW + "[+] Project Guide : " + Fore.WHITE + "Prof. J. R. Mahajan")
    print(Fore.YELLOW + "[+] Department     : " + Fore.WHITE + "Computer Engineering")
    print(Fore.YELLOW + "[+] Institute      : " + Fore.WHITE + "Savitribai Phule Pune University")
    print(Fore.YELLOW + "[+] Developer      : " + Fore.WHITE + "Viraj B. Kadam")

    print(Fore.CYAN + "-"*68)
    print(Fore.GREEN + " " * 26 + "WELCOME TO DarkReaper")
    print(Fore.CYAN + "-"*68)

    print(Fore.WHITE + ">> " + Fore.YELLOW + "Description :")
    print(Fore.LIGHTWHITE_EX + "   DarkReaper is an advanced OSINT framework that automates")
    print("   data gathering from surface web and dark web sources.")
    print("   It integrates AI-driven modules for intelligence analysis,")
    print("   ensuring enhanced efficiency and accuracy in investigation.\n")

    print(Fore.CYAN + "-"*68)
    print(Fore.WHITE + ">> " + Fore.YELLOW + "Features :")
    print(Fore.LIGHTWHITE_EX + "   [1] Email Lookup")
    print("   [2] Phone Number Lookup")
    print("   [3] IP Address Analysis")
    print("   [4] Username Tracing")
    print("   [5] Image & Metadata Extraction")
    print("   [6] Dark Web Intelligence")
    #print("   [7] AI-powered Output Handler\n")

    print(Fore.CYAN + "-"*68)
    print(Fore.WHITE + ">> " + Fore.YELLOW + "System Info :")
    print(Fore.LIGHTWHITE_EX + "   Version      : 1.0 (Stable)")
    print("   Platform     : Linux")
    print("   Language     : Python 3")
    print("   Mode         : CLI-based Interface")
    print(Fore.CYAN + "-"*68)
    print(Fore.YELLOW + ">> Loading modules..." + Fore.LIGHTBLACK_EX + " please wait...\n")
    print(Fore.CYAN + "="*68)


if __name__ == "__main__":
    interface()
    


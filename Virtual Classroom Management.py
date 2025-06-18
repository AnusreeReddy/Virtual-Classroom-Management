import sys
from collections import deque

# Cross-platform getpass with '*' masking
try:
    import msvcrt  
except ImportError:
    import tty
    import termios  

def getpass_with_mask(prompt="Password: "):
    print(prompt, end='', flush=True)
    password = ''
    try:
        if sys.platform == 'win32':
            while True:
                ch = msvcrt.getch()
                if ch in {b'\r', b'\n'}:
                    print()
                    break
                elif ch == b'\x08':
                    if password:
                        password = password[:-1]
                        print('\b \b', end='', flush=True)
                elif ch == b'\x03':
                    raise KeyboardInterrupt
                else:
                    password += ch.decode('utf-8')
                    print('*', end='', flush=True)
        else:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                while True:
                    ch = sys.stdin.read(1)
                    if ch in {'\n', '\r'}:
                        print()
                        break
                    elif ch == '\x7f':
                        if password:
                            password = password[:-1]
                            print('\b \b', end='', flush=True)
                    elif ch == '\x03':
                        raise KeyboardInterrupt
                    else:
                        password += ch
                        print('*', end='', flush=True)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(1)
    return password

# Global stores
users = []
questions = deque()
answered_questions = deque()
quizzes = []
student_scores = {}

# Register user
def register_user(username, password, role):
    if not username or not password:
        print("Username and password cannot be empty.")
        return
    user = {"username": username, "password": password, "role": role, "attendance": False}
    users.append(user)
    if role == "student":
        student_scores[username] = {"score": 0, "grade": "N/A"}
    print(f"{role.capitalize()} {username} registered successfully.")

# Authenticate
def authenticate_user(role):
    username = input(f"Enter {role} username: ")
    password = getpass_with_mask(f"Enter {role} password: ")
    for user in users:
        if user["username"] == username and user["password"] == password and user["role"] == role:
            print(f"{role.capitalize()} authentication successful.")
            return user
    print(f"{role.capitalize()} authentication failed.")
    return None

# Teacher creates quiz
def create_quiz():
    quiz = []
    try:
        num = int(input("How many questions to add? "))
    except ValueError:
        print("Invalid number.")
        return
    for i in range(num):
        question = input(f"Enter question {i+1}: ")
        options = [input(f"Option {chr(65+j)}: ") for j in range(4)]
        correct = input("Enter correct option (A/B/C/D): ").upper()
        quiz.append({"question": question, "options": options, "correct_answer": correct})
    quizzes.append(quiz)
    print("Quiz created successfully.")

# Add default quiz at startup
def load_default_quiz():
    default_quiz = [
        {
            "question": "What is 7 × 8?",
            "options": ["54", "56", "58", "64"],
            "correct_answer": "B"
        },
        {
            "question": "What planet is known as the Red Planet?",
            "options": ["Earth", "Mars", "Jupiter", "Venus"],
            "correct_answer": "B"
        },
        {
            "question": "What is the past tense of 'go'?",
            "options": ["goed", "goes", "went", "going"],
            "correct_answer": "C"
        },
        {
            "question": "Who was the first President of the USA?",
            "options": ["Abraham Lincoln", "George Washington", "John Adams", "Thomas Jefferson"],
            "correct_answer": "B"
        },
        {
            "question": "Which is the largest ocean?",
            "options": ["Atlantic", "Indian", "Pacific", "Arctic"],
            "correct_answer": "C"
        }
    ]
    quizzes.append(default_quiz)

# Ask question
def ask_question(student_name, question):
    questions.append(question)
    print(f"{student_name} asked: {question}")

# Answer question
def answer_question():
    if not questions:
        print("No questions to answer.")
        return
    q = questions.popleft()
    print(f"Q: {q}")
    a = input("Your answer: ")
    answered_questions.append((q, a))
    print("Answer recorded.")

# Take quiz
def take_quiz(student_name):
    if not quizzes:
        print("No quizzes available.")
        return
    quiz = quizzes[-1]
    score = 0
    for q in quiz:
        print("\n" + q["question"])
        for i, opt in enumerate(q["options"]):
            print(f"{chr(65+i)}. {opt}")
        ans = input("Your answer (A/B/C/D): ").upper()
        if ans == q["correct_answer"]:
            score += 20
    student_scores[student_name]["score"] += score
    assign_grade(student_name)
    print(f"Quiz completed. Score: {score}")

# Assign grade
def assign_grade(student_name):
    score = student_scores[student_name]["score"]
    if score >= 90:
        grade = "A"
    elif score >= 75:
        grade = "B"
    elif score >= 50:
        grade = "C"
    else:
        grade = "D"
    student_scores[student_name]["grade"] = grade
    print(f"{student_name}'s grade: {grade}")

# View performance
def view_performance_summary():
    print("\n--- Performance Summary ---")
    for s, d in student_scores.items():
        print(f"{s}: Score = {d['score']}, Grade = {d['grade']}")

# Mark attendance
def mark_attendance():
    for u in users:
        if u["role"] == "student":
            u["attendance"] = True
            print(f"Marked: {u['username']}")

# Check attendance
def check_attendance(student_name):
    for u in users:
        if u["username"] == student_name:
            status = "marked" if u["attendance"] else "not marked"
            print(f"Attendance: {status}")

# View answered questions
def view_answered_questions():
    if not answered_questions:
        print("No answered questions.")
        return
    print("\n--- Answered Questions ---")
    for q, a in answered_questions:
        print(f"Q: {q}\nA: {a}")

# Main loop
def main():
    load_default_quiz()  # Load quiz on startup
    while True:
        print("\n--- Main Menu ---")
        print("1. Register Student\n2. Register Teacher\n3. Login Student\n4. Login Teacher\n5. Exit")
        ch = input("Choice: ")

        if ch == '1':
            u = input("Student username: ")
            p = getpass_with_mask("Student password: ")
            register_user(u, p, "student")

        elif ch == '2':
            u = input("Teacher username: ")
            p = getpass_with_mask("Teacher password: ")
            register_user(u, p, "teacher")

        elif ch == '3':
            user = authenticate_user("student")
            if user:
                while True:
                    print("\nStudent Menu:\n1. Ask Question\n2. Take Quiz\n3. Check Attendance\n4. View Performance\n5. View Answers\n6. Logout")
                    sc = input("Choice: ")
                    if sc == '1':
                        q = input("Enter question: ")
                        ask_question(user["username"], q)
                    elif sc == '2':
                        take_quiz(user["username"])
                    elif sc == '3':
                        check_attendance(user["username"])
                    elif sc == '4':
                        view_performance_summary()
                    elif sc == '5':
                        view_answered_questions()
                    elif sc == '6':
                        break

        elif ch == '4':
            user = authenticate_user("teacher")
            if user:
                while True:
                    print("\nTeacher Menu:\n1. Answer Question\n2. Create Quiz\n3. Mark Attendance\n4. View Performance\n5. Logout")
                    tc = input("Choice: ")
                    if tc == '1':
                        answer_question()
                    elif tc == '2':
                        create_quiz()
                    elif tc == '3':
                        mark_attendance()
                    elif tc == '4':
                        view_performance_summary()
                    elif tc == '5':
                        break

        elif ch == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()

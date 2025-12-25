import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import random


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Quiz Game")
        self.root.geometry("500x400")
        self.root.configure(bg="#f5f5f5")

        self.score = 0
        self.question_index = 0
        self.time_limit = 10
        self.time_left = self.time_limit
        self.timer_id = None
        self.user_answers = []

        # ✅ Load 100 random questions
        self.questions = self.load_questions()
        random.shuffle(self.questions)  # shuffle question order

        # 🎨 Fonts
        self.font_title = ("Helvetica", 16, "bold")
        self.font_question = ("Helvetica", 14)
        self.font_option = ("Helvetica", 12)

        # Timer Label
        self.timer_label = tk.Label(
            root, text=f"Time left: {self.time_left} seconds",
            font=self.font_question, bg="#f5f5f5"
        )
        self.timer_label.pack(pady=10)

        # Content Frame
        self.content_frame = tk.Frame(root, bg="#ffffff", bd=2, relief="flat")
        self.content_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Question Label
        self.question_label = tk.Label(
            self.content_frame, text="", font=self.font_title, wraplength=400, bg="#ffffff"
        )
        self.question_label.pack(pady=20)

        # Options
        self.selected_option = tk.IntVar(value=-1)
        self.option_buttons = []
        for i in range(4):
            btn = ttk.Radiobutton(
                self.content_frame, text="", variable=self.selected_option, value=i,
                style="TRadiobutton", command=self.enable_submit
            )
            btn.pack(anchor="w", padx=20, pady=5)
            self.option_buttons.append(btn)

        # Submit Button
        self.submit_button = ttk.Button(
            root, text="Submit", command=self.check_answer, state="disabled"
        )
        self.submit_button.pack(pady=20)

        self.display_question()

    # ✅ Load or create 100 random questions
    def load_questions(self):
        conn = sqlite3.connect("quiz.db")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                option1 TEXT,
                option2 TEXT,
                option3 TEXT,
                option4 TEXT,
                answer INTEGER
            )
        """)

        # Check count
        cursor.execute("SELECT COUNT(*) FROM questions")
        count = cursor.fetchone()[0]

        # Insert base data if empty
        if count == 0:
            base_questions = [
                ("What is the capital of India?", "Delhi", "Mumbai", "Kolkata", "Chennai", 0),
                ("Which planet is known as the Red Planet?", "Earth", "Venus", "Mars", "Jupiter", 2),
                ("Who wrote 'Romeo and Juliet'?", "Charles Dickens", "William Shakespeare", "Leo Tolstoy", "Mark Twain", 1),
                ("Which is the largest ocean on Earth?", "Indian", "Atlantic", "Pacific", "Arctic", 2),
                ("Which is the smallest prime number?", "0", "1", "2", "3", 2),
                ("What gas do plants release during photosynthesis?", "Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen", 0),
                ("Who is known as the Father of the Nation in India?", "Jawaharlal Nehru", "Subhas Chandra Bose", "Mahatma Gandhi", "B. R. Ambedkar", 2),
                ("Which element has the chemical symbol ‘O’?", "Oxygen", "Gold", "Iron", "Silver", 0),
                ("How many continents are there in the world?", "5", "6", "7", "8", 2),
                ("Which is the fastest land animal?", "Lion", "Cheetah", "Tiger", "Horse", 1),
            ]

            # Duplicate and slightly modify to make 100 random questions
            random_questions = []
            for i in range(100):
                q = random.choice(base_questions)
                random_questions.append((
                    f"{q[0]} (Set {i+1})", q[1], q[2], q[3], q[4], q[5]
                ))

            cursor.executemany(
                "INSERT INTO questions (question, option1, option2, option3, option4, answer) VALUES (?, ?, ?, ?, ?, ?)",
                random_questions
            )
            conn.commit()

        # Fetch all questions
        cursor.execute("SELECT * FROM questions")
        questions = cursor.fetchall()
        conn.close()
        return questions

    def display_question(self):
        if not self.questions:
            messagebox.showerror("Error", "No questions available in the database!")
            self.root.destroy()
            return

        q = self.questions[self.question_index]
        self.question_label.config(text=f"Q{self.question_index + 1}: {q[1]}")

        for i, option in enumerate(q[2:6]):
            self.option_buttons[i].config(text=option)

        self.time_left = self.time_limit
        self.start_timer()
        self.submit_button.config(state="disabled")

    def check_answer(self):
        q = self.questions[self.question_index]
        selected = self.selected_option.get()
        self.user_answers.append((q[1], q[2:6], selected, q[6]))

        if selected == q[6]:
            self.score += 1

        self.next_question()

    def next_question(self):
        self.stop_timer()
        self.question_index += 1
        if self.question_index < len(self.questions):
            self.selected_option.set(-1)
            self.display_question()
        else:
            self.show_final_results()

    def show_final_results(self):
        self.stop_timer()

        result_window = tk.Toplevel(self.root)
        result_window.title("Quiz Results")
        result_window.geometry("600x500")
        result_window.configure(bg="#f5f5f5")

        title_label = tk.Label(
            result_window, text=f"Quiz Completed! Score: {self.score}/{len(self.questions)}",
            font=("Helvetica", 16, "bold"), bg="#f5f5f5", fg="blue"
        )
        title_label.pack(pady=10)

        frame_canvas = tk.Frame(result_window, bg="#f5f5f5")
        frame_canvas.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(frame_canvas, bg="#f5f5f5", highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f5f5f5")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for question, options, user_answer, correct_answer in self.user_answers:
            tk.Label(scrollable_frame, text=f"Q: {question}", font=("Helvetica", 12, "bold"), bg="#f5f5f5").pack(anchor="w", pady=5)

            for i, option in enumerate(options):
                if i == correct_answer:
                    color = "green" if i == user_answer else "darkgreen"
                    text = f"✅ {option} (Correct)"
                elif i == user_answer:
                    color = "red"
                    text = f"❌ {option} (Your choice)"
                else:
                    color = "black"
                    text = f"   {option}"

                tk.Label(scrollable_frame, text=text, font=("Helvetica", 11), fg=color, bg="#f5f5f5").pack(anchor="w", padx=20)

        ttk.Button(result_window, text="Close", command=result_window.destroy).pack(pady=10)

    def start_timer(self):
        self.timer_label.config(text=f"Time left: {self.time_left} seconds")
        self.time_left -= 1
        if self.time_left >= 0:
            self.timer_id = self.root.after(1000, self.start_timer)
        else:
            self.next_question()

    def stop_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def enable_submit(self):
        if self.selected_option.get() != -1:
            self.submit_button.config(state="normal")


root = tk.Tk()
quiz_app = QuizApp(root)
root.mainloop()

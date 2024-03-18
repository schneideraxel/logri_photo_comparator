import tkinter as tk
from PIL import Image, ImageTk
import os
import sys
import csv


class PropertyTaxPhotoReview:
    def __init__(self, root):
        self.root = root
        self.root.title("Enumerator/Backchecker Photo Comparator 1.0-alpha ©LoGRI 2023")
        self.pairs = []
        self.current_pair_index = 0
        self.create_ui()
        self.load_data()
        self.load_pair(0)


    def get_script_directory(self):
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        elif hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS
        else:
            return os.path.dirname(os.path.abspath(__file__))

    def load_data(self):
        script_directory = self.get_script_directory()
        file_path = os.path.join(script_directory, "input/photo_backcheck.csv")

        with open(file_path, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            rows = [row for row in reader]

            pairs_dict = {}
            for row in rows:
                caseid = row["caseid"]
                if caseid in pairs_dict:
                    pairs_dict[caseid].append(row)
                else:
                    pairs_dict[caseid] = [row]

            for caseid, rows in pairs_dict.items():
                if len(rows) == 2:
                    self.pairs.append(rows)

    def create_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.correct_button = self.create_button("Correct", self.mark_correct)
        self.wrong_button = self.create_button("Wrong", self.mark_wrong)
        self.back_button = self.create_button("Go Back", self.go_back)
        self.next_button = self.create_button("Next", self.load_next_pair)
        self.caseid_label = self.create_label("Case")
        self.image_label = None

    def create_button(self, text, command):
        button = tk.Button(self.root, text=text, command=command)
        button.pack(side="left")
        return button

    def create_label(self, text):
        label = tk.Label(self.root, text=text)
        label.pack()
        return label

    def load_pair(self, index):
        if 0 <= index < len(self.pairs):
            pair = self.pairs[index]
            self.current_pair_index = index
            self.display_photos(pair)
        else:
            self.save_data()
            self.display_message("All photos have been reviewed. Data saved.")

    def display_photos(self, pair):
        caseid = pair[0]["caseid"]
        self.caseid_label.config(text=f"Case: {caseid}")

        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Label) and widget != self.caseid_label:
                widget.destroy()

        for row in pair:
            enumerator_image_path = row.get("front_image", "")

            if enumerator_image_path:
                program_directory = self.get_script_directory()
                enumerator_image_path = os.path.join(program_directory, enumerator_image_path)

                try:
                    enumerator_image = Image.open(enumerator_image_path)

                    screen_width = self.root.winfo_screenwidth()
                    screen_height = self.root.winfo_screenheight()
                    resized_image = enumerator_image.resize((screen_width // 3, screen_height // 3))

                    enumerator_image_widget = ImageTk.PhotoImage(resized_image)
                    self.image_label = tk.Label(self.root, image=enumerator_image_widget)
                    self.image_label.image = enumerator_image_widget
                    self.image_label.pack()

                    self.root.update()
                except FileNotFoundError:
                    self.display_message(f"Image not found: {enumerator_image_path}")
            else:
                self.display_message("No media file")

    def display_message(self, message):
        message_label = self.create_label(message)

    def mark_correct(self):
        self.save_current_pair("Correct")
        self.load_next_pair()

    def mark_wrong(self):
        self.save_current_pair("Wrong")
        self.load_next_pair()

    def go_back(self):
        self.load_pair(self.current_pair_index - 1)

    def load_next_pair(self):
        if self.current_pair_index < len(self.pairs) - 1:
            self.current_pair_index += 1
            pair = self.pairs[self.current_pair_index]
            self.load_pair(self.current_pair_index)
        else:
            self.save_data()
            self.display_message("All photos have been reviewed. Data saved.")

    def save_current_pair(self, status):
        if 0 <= self.current_pair_index < len(self.pairs):
            pair = self.pairs[self.current_pair_index]

            for row in pair:
                row["status"] = status

        self.save_data()

    def save_data(self):
        script_directory = self.get_script_directory()
        output_file_path = os.path.join(script_directory, "output/completed_review.csv")

        with open(output_file_path, mode="w", newline="") as file:
            fieldnames = self.pairs[0][0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for pair in self.pairs:
                for row in pair:
                    writer.writerow(row)


if __name__ == "__main__":
    root = tk.Tk()
    app = PropertyTaxPhotoReview(root)
    root.mainloop()
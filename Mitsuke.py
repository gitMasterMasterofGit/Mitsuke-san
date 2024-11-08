import tkinter as tk

# Create the main window
root = tk.Tk()

# Set the title of the window
root.title("My First Tkinter App")

# Set the window size
root.geometry("400x300")

# Create a label widget
label = tk.Label(root, text="Hello, Tkinter!", font=("Arial", 24))
label.pack(pady=20)  # Add padding around the label

# Create a button widget
def on_button_click():
    label.config(text="Button Clicked!")

button = tk.Button(root, text="Click Me", command=on_button_click)
button.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()

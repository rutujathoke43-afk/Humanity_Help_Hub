import customtkinter as ctk
from tkinter import messagebox
import sqlite3


# =========================================================
# APP SETTINGS
# =========================================================

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# =========================================================
# DATABASE
# =========================================================

def create_database():
    conn = sqlite3.connect("humanity_help.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            help_type TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


create_database()


# =========================================================
# SUBMIT REQUEST
# =========================================================

def submit_request():

    name = name_entry.get().strip()
    help_type = help_entry.get()
    description = description_entry.get("1.0", "end").strip()

    if name == "" or help_type == "Select Type of Help" or description == "":
        messagebox.showwarning(
            "Missing Information",
            "Please fill all the fields."
        )
        return

    conn = sqlite3.connect("humanity_help.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO requests (name, help_type, description)
        VALUES (?, ?, ?)
        """,
        (name, help_type, description)
    )

    conn.commit()
    conn.close()

    messagebox.showinfo(
        "Request Submitted",
        f"Thank you {name}!\n\n"
        "Your help request has been submitted successfully. ❤️"
    )

    name_entry.delete(0, "end")
    help_entry.set("Select Type of Help")
    description_entry.delete("1.0", "end")


# =========================================================
# VIEW REQUESTS
# =========================================================

def view_requests():

    window = ctk.CTkToplevel(root)
    window.title("All Help Requests")
    window.geometry("750x600")
    window.resizable(False, False)

    title = ctk.CTkLabel(
        window,
        text="📋 All Help Requests",
        font=("Arial", 26, "bold")
    )
    title.pack(pady=25)

    conn = sqlite3.connect("humanity_help.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, help_type, description FROM requests"
    )

    requests = cursor.fetchall()
    conn.close()

    if not requests:
        ctk.CTkLabel(
            window,
            text="No help requests available yet.",
            font=("Arial", 18)
        ).pack(pady=50)
        return

    scroll = ctk.CTkScrollableFrame(
        window,
        width=680,
        height=450
    )
    scroll.pack(padx=20, pady=10, fill="both", expand=True)

    for request in requests:

        card = ctk.CTkFrame(
            scroll,
            corner_radius=15
        )
        card.pack(
            fill="x",
            padx=10,
            pady=10
        )

        ctk.CTkLabel(
            card,
            text=f"🆔 Request #{request[0]}",
            font=("Arial", 17, "bold")
        ).pack(anchor="w", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            card,
            text=f"👤 Name: {request[1]}",
            font=("Arial", 14)
        ).pack(anchor="w", padx=20, pady=3)

        ctk.CTkLabel(
            card,
            text=f"🆘 Help Type: {request[2]}",
            font=("Arial", 14)
        ).pack(anchor="w", padx=20, pady=3)

        ctk.CTkLabel(
            card,
            text=f"📝 {request[3]}",
            font=("Arial", 14),
            wraplength=600,
            justify="left"
        ).pack(anchor="w", padx=20, pady=(3, 15))


# =========================================================
# SEARCH REQUESTS
# =========================================================

def search_requests():

    search_window = ctk.CTkToplevel(root)
    search_window.title("Search Help Requests")
    search_window.geometry("700x600")
    search_window.resizable(False, False)

    ctk.CTkLabel(
        search_window,
        text="🔎 Search Help Requests",
        font=("Arial", 26, "bold")
    ).pack(pady=25)

    search_entry = ctk.CTkEntry(
        search_window,
        width=450,
        height=45,
        placeholder_text="Enter person's name..."
    )
    search_entry.pack(pady=10)

    results_frame = ctk.CTkScrollableFrame(
        search_window,
        width=620,
        height=380
    )
    results_frame.pack(pady=20, padx=20, fill="both", expand=True)

    def perform_search():

        for widget in results_frame.winfo_children():
            widget.destroy()

        name = search_entry.get().strip()

        conn = sqlite3.connect("humanity_help.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT name, help_type, description
            FROM requests
            WHERE name LIKE ?
            """,
            ("%" + name + "%",)
        )

        results = cursor.fetchall()
        conn.close()

        if not results:

            ctk.CTkLabel(
                results_frame,
                text="❌ No requests found.",
                font=("Arial", 18)
            ).pack(pady=30)

            return

        for result in results:

            card = ctk.CTkFrame(
                results_frame,
                corner_radius=15
            )
            card.pack(
                fill="x",
                padx=10,
                pady=10
            )

            ctk.CTkLabel(
                card,
                text=f"👤 {result[0]}",
                font=("Arial", 17, "bold")
            ).pack(anchor="w", padx=20, pady=(15, 5))

            ctk.CTkLabel(
                card,
                text=f"🆘 {result[1]}",
                font=("Arial", 14)
            ).pack(anchor="w", padx=20, pady=3)

            ctk.CTkLabel(
                card,
                text=f"📝 {result[2]}",
                font=("Arial", 14),
                wraplength=550,
                justify="left"
            ).pack(anchor="w", padx=20, pady=(3, 15))

    ctk.CTkButton(
        search_window,
        text="🔍 Search",
        width=200,
        height=40,
        command=perform_search
    ).pack(pady=5)


# =========================================================
# CLEAR FORM
# =========================================================

def clear_form():

    name_entry.delete(0, "end")
    help_entry.set("Select Type of Help")
    description_entry.delete("1.0", "end")


# =========================================================
# MAIN WINDOW
# =========================================================

root = ctk.CTk()

root.title("Humanity Help Hub")
root.geometry("1000x700")
root.minsize(900, 650)


# =========================================================
# SIDEBAR
# =========================================================

sidebar = ctk.CTkFrame(
    root,
    width=230,
    corner_radius=0
)

sidebar.pack(
    side="left",
    fill="y"
)

sidebar.pack_propagate(False)


# Logo

ctk.CTkLabel(
    sidebar,
    text="🌍",
    font=("Arial", 55)
).pack(pady=(45, 5))

ctk.CTkLabel(
    sidebar,
    text="Humanity\nHelp Hub",
    font=("Arial", 25, "bold"),
    justify="center"
).pack(pady=5)

ctk.CTkLabel(
    sidebar,
    text="Together We Can\nMake A Difference ❤️",
    font=("Arial", 13),
    justify="center"
).pack(pady=(5, 40))


# Sidebar buttons

ctk.CTkButton(
    sidebar,
    text="🏠  Home",
    height=45,
    corner_radius=10,
    command=lambda: name_entry.focus()
).pack(fill="x", padx=20, pady=8)

ctk.CTkButton(
    sidebar,
    text="📋  View Requests",
    height=45,
    corner_radius=10,
    command=view_requests
).pack(fill="x", padx=20, pady=8)

ctk.CTkButton(
    sidebar,
    text="🔎  Search Requests",
    height=45,
    corner_radius=10,
    command=search_requests
).pack(fill="x", padx=20, pady=8)

ctk.CTkButton(
    sidebar,
    text="🧹  Clear Form",
    height=45,
    corner_radius=10,
    command=clear_form
).pack(fill="x", padx=20, pady=8)


ctk.CTkLabel(
    sidebar,
    text="",
).pack(expand=True)


ctk.CTkLabel(
    sidebar,
    text="❤️ Help • Hope • Humanity",
    font=("Arial", 12)
).pack(pady=25)


# =========================================================
# MAIN CONTENT
# =========================================================

main_frame = ctk.CTkFrame(
    root,
    corner_radius=0,
    fg_color="transparent"
)

main_frame.pack(
    side="right",
    fill="both",
    expand=True,
    padx=30,
    pady=25
)


# =========================================================
# HEADER
# =========================================================

ctk.CTkLabel(
    main_frame,
    text="Welcome to Humanity Help Hub 🌍",
    font=("Arial", 32, "bold")
).pack(anchor="w", pady=(10, 5))

ctk.CTkLabel(
    main_frame,
    text="A platform where people can request help and support each other.",
    font=("Arial", 15)
).pack(anchor="w", pady=(0, 25))


# =========================================================
# INFORMATION CARDS
# =========================================================

cards_frame = ctk.CTkFrame(
    main_frame,
    fg_color="transparent"
)

cards_frame.pack(fill="x", pady=5)

card1 = ctk.CTkFrame(
    cards_frame,
    height=100,
    corner_radius=15
)
card1.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 8)
)

ctk.CTkLabel(
    card1,
    text="🆘",
    font=("Arial", 30)
).pack(pady=(12, 0))

ctk.CTkLabel(
    card1,
    text="Request Help",
    font=("Arial", 15, "bold")
).pack()


card2 = ctk.CTkFrame(
    cards_frame,
    height=100,
    corner_radius=15
)
card2.pack(
    side="left",
    fill="both",
    expand=True,
    padx=8
)

ctk.CTkLabel(
    card2,
    text="🤝",
    font=("Arial", 30)
).pack(pady=(12, 0))

ctk.CTkLabel(
    card2,
    text="Help Others",
    font=("Arial", 15, "bold")
).pack()


card3 = ctk.CTkFrame(
    cards_frame,
    height=100,
    corner_radius=15
)
card3.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(8, 0)
)

ctk.CTkLabel(
    card3,
    text="❤️",
    font=("Arial", 30)
).pack(pady=(12, 0))

ctk.CTkLabel(
    card3,
    text="Spread Humanity",
    font=("Arial", 15, "bold")
).pack()


# =========================================================
# REQUEST FORM
# =========================================================

form_frame = ctk.CTkFrame(
    main_frame,
    corner_radius=20
)

form_frame.pack(
    fill="both",
    expand=True,
    pady=20
)


ctk.CTkLabel(
    form_frame,
    text="🆘 Request Help",
    font=("Arial", 24, "bold")
).pack(anchor="w", padx=30, pady=(25, 15))


# Name

ctk.CTkLabel(
    form_frame,
    text="Your Name",
    font=("Arial", 14, "bold")
).pack(anchor="w", padx=30, pady=(5, 5))

name_entry = ctk.CTkEntry(
    form_frame,
    height=42,
    placeholder_text="Enter your full name"
)

name_entry.pack(
    fill="x",
    padx=30,
    pady=(0, 12)
)


# Help Type

ctk.CTkLabel(
    form_frame,
    text="Type of Help",
    font=("Arial", 14, "bold")
).pack(anchor="w", padx=30, pady=5)

help_entry = ctk.CTkComboBox(
    form_frame,
    height=42,
    values=[
        "Food",
        "Medical",
        "Education",
        "Clothes",
        "Emergency",
        "Other"
    ]
)

help_entry.set("Select Type of Help")

help_entry.pack(
    fill="x",
    padx=30,
    pady=(0, 12)
)


# Description

ctk.CTkLabel(
    form_frame,
    text="Description",
    font=("Arial", 14, "bold")
).pack(anchor="w", padx=30, pady=5)

description_entry = ctk.CTkTextbox(
    form_frame,
    height=80,
    corner_radius=10
)

description_entry.pack(
    fill="x",
    padx=30,
    pady=(0, 15)
)



# Submit

ctk.CTkButton(
    form_frame,
    text="❤️  Submit Help Request",
    height=45,
    corner_radius=12,
    font=("Arial", 15, "bold"),
    command=submit_request
).pack(
    fill="x",
    padx=30,
    pady=(5, 25)
)


# =========================================================
# START APP
# =========================================================

root.mainloop()
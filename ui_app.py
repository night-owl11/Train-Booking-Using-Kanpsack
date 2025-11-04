# ui_app.py
import tkinter as tk
from tkinter import messagebox
from train_booking_logic import Group, allocate_seats, handle_cancellation, TOTAL_SEATS, STATIONS

class TrainBookingApp:
    def __init__(self, master):
        self.master = master
        master.title("🚂 Knapsack Train Booking Optimizer")
        
        self.groups = []
        self.fare_per_section = tk.DoubleVar(value=5.0) # Default value
        
        self.create_widgets()

    def create_widgets(self):
        # --- Frame for Initial Setup ---
        setup_frame = tk.LabelFrame(self.master, text="1. Setup & Group Entry", padx=10, pady=10)
        setup_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        tk.Label(setup_frame, text=f"Max Train Seats: {TOTAL_SEATS}").grid(row=0, column=0, columnspan=2, pady=5)
        
        tk.Label(setup_frame, text="Fare Per Section ($):").grid(row=1, column=0, sticky="w")
        tk.Entry(setup_frame, textvariable=self.fare_per_section, width=10).grid(row=1, column=1, sticky="w")
        
        tk.Label(setup_frame, text="Route (e.g., AB, AC):").grid(row=2, column=0, sticky="w")
        self.route_entry = tk.Entry(setup_frame, width=5)
        self.route_entry.grid(row=2, column=1, sticky="w")
        
        tk.Label(setup_frame, text="Members (Seats):").grid(row=3, column=0, sticky="w")
        self.members_entry = tk.Entry(setup_frame, width=5)
        self.members_entry.grid(row=3, column=1, sticky="w")
        
        tk.Button(setup_frame, text="Add Group", command=self.add_group, bg="lightgreen").grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")
        tk.Button(setup_frame, text="Run Allocation", command=self.run_allocation, bg="lightblue").grid(row=5, column=0, columnspan=2, pady=5, sticky="ew")

        # --- Groups List Display ---
        self.groups_listbox = tk.Listbox(setup_frame, height=5, width=40)
        self.groups_listbox.grid(row=6, column=0, columnspan=2, pady=5)
        
        # --- Frame for Results ---
        self.results_frame = tk.LabelFrame(self.master, text="2. Allocation Summary (Knapsack Result)", padx=10, pady=10)
        self.results_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.summary_label = tk.Label(self.results_frame, text="Press 'Run Allocation' to see results.")
        self.summary_label.grid(row=0, column=0, columnspan=4, sticky="w", pady=5)
        
        # Simple Table Headers
        tk.Label(self.results_frame, text="ID | Route | Members | Fare | Status", font=('TkDefaultFont', 9, 'bold')).grid(row=1, column=0, columnspan=4, sticky="w")
        
        # Results Listbox
        self.results_listbox = tk.Listbox(self.results_frame, height=8, width=50)
        self.results_listbox.grid(row=2, column=0, columnspan=4, pady=5)

        # --- Frame for Cancellation ---
        cancel_frame = tk.LabelFrame(self.master, text="3. Cancellation", padx=10, pady=10)
        cancel_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        tk.Label(cancel_frame, text="Group ID to Cancel:").grid(row=0, column=0, sticky="w")
        self.cancel_id_entry = tk.Entry(cancel_frame, width=5)
        self.cancel_id_entry.grid(row=0, column=1, sticky="w")
        
        tk.Button(cancel_frame, text="Cancel Booking", command=self.cancel_booking, bg="salmon").grid(row=0, column=2, padx=10)


    def add_group(self):
        try:
            route = self.route_entry.get().upper()
            members = int(self.members_entry.get())
            fare = self.fare_per_section.get()

            if len(route) != 2 or route[0] not in STATIONS or route[1] not in STATIONS or members <= 0:
                 messagebox.showerror("Input Error", "Invalid Route (e.g., AB) or Members (must be > 0).")
                 return
            
            new_group = Group(route, members, fare)
            self.groups.append(new_group)
            
            # Update the Groups Listbox
            self.groups_listbox.insert(tk.END, f"ID {new_group.id} | {route} | {members} members | ${new_group.total_fare:.2f}")

            # Clear entry fields
            self.route_entry.delete(0, tk.END)
            self.members_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for members.")

    def run_allocation(self):
        if not self.groups:
            messagebox.showinfo("Allocation", "Please add groups before running allocation.")
            return

        try:
            fare = self.fare_per_section.get()
            if fare <= 0:
                messagebox.showerror("Input Error", "Fare per section must be greater than zero.")
                return

            # Call the Knapsack-like allocation function
            allocated, waiting, revenue, remaining_seats = allocate_seats(self.groups, fare)
            
            self.results_listbox.delete(0, tk.END) # Clear previous results
            
            all_groups_sorted = allocated + waiting
            all_groups_sorted.sort(key=lambda g: g.id) # Sort back by ID for stable display

            # Populate Results Listbox
            for group in all_groups_sorted:
                status = "BOOKED" if group.is_booked else "WAITING"
                line = f"{group.id: <3}| {group.route: <4}| {group.members: <6} | {group.total_fare:.2f} | {status}"
                self.results_listbox.insert(tk.END, line)

            # Update Summary Label
            # Updated text to remove mention of overbooking
            summary = (
                f"Allocation Capacity: {TOTAL_SEATS}.\n"
                f"Total Revenue: **${revenue:.2f}** | Remaining Capacity: **{remaining_seats}**"
            )
            self.summary_label.config(text=summary)

        except Exception as e:
            messagebox.showerror("Processing Error", f"An error occurred during allocation: {e}")

    def cancel_booking(self):
        try:
            cancel_id = int(self.cancel_id_entry.get())
            
            message, group_id_cancelled = handle_cancellation(self.groups, cancel_id)
            messagebox.showinfo("Cancellation Status", message)
            
            if group_id_cancelled is not None:
                # Re-run allocation to update the results display with the new state
                self.run_allocation()

            self.cancel_id_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid integer for Group ID.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainBookingApp(root)
    root.mainloop()
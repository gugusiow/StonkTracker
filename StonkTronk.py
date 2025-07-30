import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import yfinance as yf

APP_VERSION = "1.0.0"

class StockTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("StonkTronk")

        self.label = ttk.Label(root, text="Enter stock ticker:")
        self.label.pack(pady=20)
        self.label.config(font=("Arial", 20, "bold"))

        self.entry = ttk.Entry(root)
        self.entry.pack()

        self.button = ttk.Button(root, text="Get Stock Data", command=self.get_stock_data)
        self.button.pack(pady=10)

        self.output = ttk.Text(root, height=10, width=50)
        self.output.pack()
        self.version_label = ttk.Label(root, text=f"Stock Tracker v{APP_VERSION}")
        self.version_label.pack(pady=70)

    # app logic # 
    def get_stock_data(self):
        ticker = self.entry.get().upper()
        if not ticker:
            messagebox.showwarning("Input Error", "Please enter a stock ticker.")
            return

        stock = yf.Ticker(ticker)
        try:
            data = stock.history(period="1d")
            if data.empty:
                raise Exception("No data found")

            current_price = data['Close'].iloc[-1]
            volume = data['Volume'].iloc[-1]
            info = stock.info
            high_52w = info.get('fiftyTwoWeekHigh', None)

            is_price_high = None
            if high_52w:
                is_price_high = current_price >= 0.95 * high_52w

            self.output.delete('1.0', tk.END)
            self.output.insert(tk.END, f"Ticker: {ticker}\n")
            self.output.insert(tk.END, f"Price: ${current_price:.2f}\n")
            self.output.insert(tk.END, f"Volume: {volume}\n")
            if high_52w:
                self.output.insert(tk.END, f"52 Week High: ${high_52w:.2f}\n")
                self.output.insert(tk.END, f"Near High? {'Yes' if is_price_high else 'No'}\n")
            else:
                self.output.insert(tk.END, "52 Week High: N/A\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get data for {ticker}.\n{e}")

if __name__ == "__main__":
    root = ttk.Window(themename='darkly')
    root.geometry("700x600")
    app = StockTrackerApp(root)
    root.mainloop()
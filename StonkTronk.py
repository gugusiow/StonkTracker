import tkinter as tk
from tkinter import messagebox, ttk as tk_ttk
from tkinter.font import Font
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import yfinance as yf
import json
import os
from datetime import datetime

# important widgets like label, buttons, treeviews, etc

APP_VERSION = "1.1.0"
PORTFOLIO_FILE = "portfolio.json"

class StockTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("StonkTronk - Personal Investment Tracker") # app title
        
        # Load saved portfolio
        self.portfolio = self.load_portfolio()  
        
        # Create the main notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_portfolio_tab()
        self.create_lookup_tab()
        # self.create_financialNews_tab()
        
        # Version label at bottom
        self.version_label = ttk.Label(root, text=f"StonkTronk v{APP_VERSION}")
        self.version_label.pack(pady=10)

    # Portfolio management methods
    def load_portfolio(self):
        """Load portfolio from JSON file"""
        if os.path.exists(PORTFOLIO_FILE):
            try:
                with open(PORTFOLIO_FILE, 'r') as f:    # open the json in r mode
                    return json.load(f)
            except:
                return []
        return []
    
    def save_portfolio(self):
        """Save portfolio to JSON file"""
        try:
            with open(PORTFOLIO_FILE, 'w') as f:    # open json in write mode and save the newly added/removed stocks
                json.dump(self.portfolio, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save portfolio: {e}")
    
    def create_portfolio_tab(self):
        """Create the portfolio tab"""
        portfolio_frame = ttk.Frame(self.notebook)
        self.notebook.add(portfolio_frame, text="Portfolio")
        
        # Title
        title_label = ttk.Label(portfolio_frame, text="My Portfolio", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=10)
        
        # Add stock section
        customLabel1 = ttk.Label(portfolio_frame,text="Add Stock to Portfolio", font=("Helvetica", 14))
        add_frame = ttk.LabelFrame(portfolio_frame, labelwidget=customLabel1, padding=10)
        add_frame.pack(fill='x', padx=10, pady=5)
        
        # Input fields frame
        input_frame = ttk.Frame(add_frame)
        input_frame.pack(fill='x')
        
        ttk.Label(input_frame, text="Ticker:", font=("", 10)).grid(row=0, column=0, sticky='e', padx=5)
        self.portfolio_ticker_entry = ttk.Entry(input_frame, width=10)
        self.portfolio_ticker_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(input_frame, text="Shares:", font=("", 10)).grid(row=0, column=2, sticky='e', padx=5)
        self.shares_entry = ttk.Entry(input_frame, width=10)
        self.shares_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(input_frame, text="Purchase Price:", font=("", 10)).grid(row=0, column=4, sticky='e', padx=5)
        self.price_entry = ttk.Entry(input_frame, width=10)
        self.price_entry.grid(row=0, column=5, padx=5)
        
        # Buttons frame
        button_frame = ttk.Frame(add_frame)
        button_frame.pack(pady=10)
        
        # buttonFonts = Font(family='Helvetica', size = 10)
        ttk.Style().configure(style="success.TButton", foreground="white", background="#5cb85c", font=("Helvetica", 10, "bold"))
        add_button = ttk.Button(button_frame, text="Add to Portfolio", command=self.add_to_portfolio, bootstyle="success")
        add_button.pack(side='left', padx=5)
        
        ttk.Style().configure(style="info.TButton", foreground="white", background="#688ecc", font=("Helvetica", 10, "bold"))
        refresh_button = ttk.Button(button_frame, text="Refresh Prices", command=self.refresh_portfolio, bootstyle="info")
        refresh_button.pack(side='left', padx=5)
        
        # Portfolio display
        customLabel2 = ttk.Label(portfolio_frame ,text="Current Holdings", font=("Helvetica", 14))
        portfolio_display_frame = ttk.LabelFrame(portfolio_frame, labelwidget=customLabel2, padding=10)
        portfolio_display_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create treeview for portfolio
        columns = ('Ticker', 'Shares', 'Purchase Price', 'Current Price', 'Value', 'Gain/Loss', '%')
        self.portfolio_tree = tk_ttk.Treeview(portfolio_display_frame, columns=columns, show='headings')
        
        # style the column headings
        ttk.Style().configure("Treeview.Heading",
                # background="#D3D3D3",  # Light gray
                foreground="white",
                font=("Helvetica", 10, "bold"),
                relief="raised")

        # Define headings
        for col in columns:
            self.portfolio_tree.heading(col, text=col)
            self.portfolio_tree.column(col, width=150, anchor='center') # add stretch = False to fix column widths
        
        # Scrollbar
        portfolio_scrollbar = tk_ttk.Scrollbar(portfolio_display_frame, orient='vertical', command=self.portfolio_tree.yview)
        self.portfolio_tree.configure(yscrollcommand=portfolio_scrollbar.set)
        self.portfolio_tree.pack(side='left', fill='both', expand=True)
        portfolio_scrollbar.pack(side='right', fill='y')
        
        # Delete button
        delete_button = ttk.Button(portfolio_display_frame, text="Remove Selected", 
                                 command=self.remove_from_portfolio, bootstyle="danger")
        delete_button.pack(pady=5)
        
        # Load initial portfolio
        self.update_portfolio_display()
    
    def create_lookup_tab(self):
        """Create the stock lookup tab"""
        lookup_frame = ttk.Frame(self.notebook)
        self.notebook.add(lookup_frame, text="Stock Lookup")
        
        # Title
        title_label = ttk.Label(lookup_frame, text="Stock Data Lookup", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=20)
        
        input_label = ttk.Label(lookup_frame, text="Enter stock ticker:", font=("Helvetica", 14))
        input_label.pack(pady=10)
        
        self.lookup_entry = ttk.Entry(lookup_frame, font=("Arial", 12))
        self.lookup_entry.pack(pady=5)
        
        ttk.Style().configure("Custom.TButton", foreground="white", background="#688ecc", font=("Helvetica", 10, "bold"))
        lookup_button = ttk.Button(lookup_frame, text="Get Stock Data", command=self.get_stock_data, style="Custom.TButton")
        lookup_button.pack(pady=10)
        
        self.lookup_output = ttk.Text(lookup_frame, height=15, width=60)
        self.lookup_output.pack(pady=10, padx=20, fill='both', expand=True)
    
    def add_to_portfolio(self):
        """Add a stock to the portfolio"""
        ticker = self.portfolio_ticker_entry.get().upper().strip()
        shares_text = self.shares_entry.get().strip()
        price_text = self.price_entry.get().strip()
        
        if not all([ticker, shares_text, price_text]):
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return
        
        try:
            shares = float(shares_text)
            purchase_price = float(price_text)
            if shares <= 0 or purchase_price <= 0:
                raise ValueError("Values must be positive")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid positive numbers for shares and price.")
            return
        
        # Check if stock exists
        stock = yf.Ticker(ticker)
        try:
            data = stock.history(period="1d")
            if data.empty:
                raise Exception("Stock not found")
        except Exception as e:
            messagebox.showerror("Error", f"Could not find stock {ticker}. Please check the ticker symbol.")
            return
        
        # Add to portfolio
        stock_entry = {
            "ticker": ticker,
            "shares": shares,
            "purchase_price": purchase_price,
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.portfolio.append(stock_entry)
        self.save_portfolio()
        self.update_portfolio_display()
        
        # Clear input fields
        self.portfolio_ticker_entry.delete(0, tk.END)
        self.shares_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        
        messagebox.showinfo("Success", f"Added {shares} shares of {ticker} to portfolio!")
    
    def remove_from_portfolio(self):
        """Remove selected stock from portfolio"""
        selected_item = self.portfolio_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a stock to remove.")
            return
        
        item = self.portfolio_tree.item(selected_item[0])
        ticker = item['values'][0]
        
        # Find and remove from portfolio
        self.portfolio = [stock for stock in self.portfolio if stock['ticker'] != ticker]
        self.save_portfolio()
        self.update_portfolio_display()
        
        messagebox.showinfo("Success", f"Removed {ticker} from portfolio!")
    
    def refresh_portfolio(self):
        """Refresh current prices for all portfolio stocks"""
        self.update_portfolio_display()
        messagebox.showinfo("Success", "Portfolio prices refreshed!")
    
    def update_portfolio_display(self):
        """Update the portfolio display with current data"""
        # Clear existing items
        for item in self.portfolio_tree.get_children():
            self.portfolio_tree.delete(item)
        
        if not self.portfolio:
            return
        
        total_value = 0
        total_cost = 0
        
        for stock in self.portfolio:
            ticker = stock['ticker']
            shares = stock['shares']
            purchase_price = stock['purchase_price']
            
            try:
                # Get current price
                yf_ticker = yf.Ticker(ticker)
                data = yf_ticker.history(period="1d")
                current_price = data['Close'].iloc[-1] if not data.empty else 0
                
                current_value = shares * current_price
                purchase_value = shares * purchase_price
                gain_loss = current_value - purchase_value
                gain_loss_percent = (gain_loss / purchase_value) * 100 if purchase_value > 0 else 0
                
                total_value += current_value
                total_cost += purchase_value
                
                # Color coding for gains/losses
                tags = ()
                if gain_loss > 0:
                    tags = ('positive',)
                elif gain_loss < 0:
                    tags = ('negative',)
                
                self.portfolio_tree.insert('', 'end', values=(
                    ticker,
                    f"{shares:.2f}",
                    f"${purchase_price:.2f}",
                    f"${current_price:.2f}",
                    f"${current_value:.2f}",
                    f"${gain_loss:.2f}",
                    f"{gain_loss_percent:.1f}%"
                ), tags=tags)
                
            except Exception as e:
                # If can't get current price, show with error
                self.portfolio_tree.insert('', 'end', values=(
                    ticker,
                    f"{shares:.2f}",
                    f"${purchase_price:.2f}",
                    "Error",
                    "Error",
                    "Error",
                    "Error"
                ))
        
        # Add total row
        if total_cost > 0:
            total_gain_loss = total_value - total_cost
            total_gain_loss_percent = (total_gain_loss / total_cost) * 100
            
            tags = ('positive',) if total_gain_loss > 0 else ('negative',) if total_gain_loss < 0 else ()
            
            self.portfolio_tree.insert('', 'end', values=(
                "TOTAL",
                "",
                "",
                "",
                f"${total_value:.2f}",
                f"${total_gain_loss:.2f}",
                f"{total_gain_loss_percent:.1f}%"
            ), tags=tags)
        
        # Configure tag colors
        self.portfolio_tree.tag_configure('positive', foreground='green')
        self.portfolio_tree.tag_configure('negative', foreground='red') 
    def get_stock_data(self):
        """Get stock data for lookup tab"""
        ticker = self.lookup_entry.get().upper().strip()
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

            self.lookup_output.delete('1.0', tk.END)
            self.lookup_output.insert(tk.END, f"Ticker: {ticker}\n")
            self.lookup_output.insert(tk.END, f"Price: ${current_price:.2f}\n")
            self.lookup_output.insert(tk.END, f"Volume: {volume:,}\n")
            if high_52w:
                self.lookup_output.insert(tk.END, f"52 Week High: ${high_52w:.2f}\n")
                self.lookup_output.insert(tk.END, f"Near High? {'Yes' if is_price_high else 'No'}\n")
            else:
                self.lookup_output.insert(tk.END, "52 Week High: N/A\n")
                
            # Additional info
            market_cap = info.get('marketCap', None)
            if market_cap:
                self.lookup_output.insert(tk.END, f"Market Cap: ${market_cap:,}\n")
            
            company_name = info.get('longName', 'N/A')
            self.lookup_output.insert(tk.END, f"Company: {company_name}\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get data for {ticker}.\n{e}")

if __name__ == "__main__":
    # can change theme of the app dependng on user's device? 
    root = ttk.Window(themename='darkly')
    root.geometry("1400x800")
    root.minsize(800, 600)
    app = StockTrackerApp(root)
    root.mainloop()
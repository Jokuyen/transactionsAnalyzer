# Johnny Nguyen
# transactionsAnalyzer
# Potential filter names for my transactions: "att, great oaks water"

'''
Tested with:
- Capital One's Credit Card
- Chase's Debit Card
'''

from displayAllTransactions import *
from monthlySpendings import *
import tkinter.filedialog
from os import getcwd
import csv

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Class variable
        self._filename = ""
        self._accountType = "Credit" # Could change in determineAccountType()
        self._transactionsList = []        
        
        '''
        # Variables for columns within csv file of Chase's Debit Card
        self._transactionDate = "Posting Date"
        self._transactionDateFormat = "%m/%d/%Y"
        self._transactionName = "Description"
        self._transactionCost = "Amount"  
        '''
        
        # Variables for columns within csv file of Capital One's Credit Card
        self._transactionDate = "Transaction Date"
        self._transactionDateFormat = "%Y-%m-%d"
        self._transactionName = "Description"
        self._transactionCost = "Debit"
        
        # Formatting
        self.minsize(400, 75)
        self.title("Transactions Analyzer")
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Functions
        self.createButtons()
        self.selectInputFile()
        self.determineAccountType()
        self.readDataIntoTransactionsList()        
        
    def createButtons(self):
        tk.Button(self, text = "Display all transactions", command= lambda: TransactionOptions(self)).grid()
        tk.Button(self, text = "Display monthly spendings for a given year", command= lambda: MonthlySpendings(self)).grid()      
        
    def selectInputFile(self):
        while ".csv" not in self._filename.lower():
            self._filename = tk.filedialog.askopenfilename(initialdir= getcwd()) 

            # If user doesn't choose a file, exit the program
            if len(self._filename) == 0:
                raise SystemExit    
            
            if ".csv" not in self._filename.lower():
                tk.messagebox.showerror("Error", "Select a '.csv' file extension", parent=self)             
        
    def determineAccountType(self):
        ''' If account is a debit card, change 'self._accountType' accordingly '''
        with open(self._filename) as filehandler:
            data = csv.DictReader(filehandler)
            for record in data:
                # If a transaction's cost is a negative number, switch 'self._accountType' to "Debit"
                if record[self._transactionCost] is not "" and float(record[self._transactionCost]) < 0:
                    self._accountType = "Debit"
                    break
        
    def readDataIntoTransactionsList(self):
        with open(self._filename) as filehandler:
            data = csv.DictReader(filehandler)
            
            if self._accountType == "Credit":
                for record in data:
                    # Skip any credit card payments
                    if record[self._transactionCost] is "":
                        continue        
                    self._transactionsList.append(record)                
            
            elif self._accountType == "Debit":
                for record in data:            
                    if float(record[self._transactionCost]) > 0:
                        continue      
                    record[self._transactionCost] = str(abs(float(record[self._transactionCost])))
                    self._transactionsList.append(record) 
    
def main():
    app = MainWindow()
    app.mainloop()

main()
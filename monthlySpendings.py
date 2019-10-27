# Johnny Nguyen
# monthlySpendings class

import matplotlib
matplotlib.use('TkAgg') # Tell matplotlib to work with Tkinter
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Tells matplotlib about Canvas object
import matplotlib.pyplot as plt 
from datetime import datetime
from statistics import mean 

class MonthlySpendings(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.transient(master)    
        
        # Class variables
        self._functionsList = [self.allTransactions, self.filteredTransactionsPrompt, self.specificTransactionPrompt]
        # Create dictionary to track spendings for each month
        self._monthsDict = {'January': 0.0, 'February': 0.0, 'March': 0.0, 'April': 0.0, 'May': 0.0, 'June': 0.0, 'July': 0.0, 
                      'August': 0.0, 'September': 0.0, 'October': 0.0, 'November': 0.0, 'December': 0.0}  
        # Sort 'transactionsList' in ascending order (so January is first instead of latest month)
        self._transactionsList = sorted(master._transactionsList, \
                                  key=lambda record: datetime.strptime(record[master._transactionDate], master._transactionDateFormat))
        
        # Formatting
        self.minsize(250, 175)
        self.title("Monthly Spendings")
        for idx in range(0, 6):
            self.grid_rowconfigure(idx, weight=1)
        self.grid_columnconfigure(0, weight=1)        
            
        # User prompt for transactions options
        inputYear = tk.IntVar()
        tk.Label(self, text = "Enter a year: ").grid()
        entryWidget = tk.Entry(self, textvariable=inputYear)
        entryWidget.grid()

        buttonOption = tk.IntVar()
        allTransactionsButton = tk.Radiobutton(self, text="Show all transactions", variable=buttonOption, value=0).grid()
        filteredTransactionButton = tk.Radiobutton(self, text="Show filtered transactions", variable=buttonOption, value=1).grid()
        specificTransactionsButton = tk.Radiobutton(self, text="Show specific transactions", variable=buttonOption, value=2).grid()
        confirmButton = tk.Button(self, text="Continue", command=lambda: \
                                  self.callFunction(master, self._monthsDict, self._transactionsList, inputYear.get(), buttonOption.get())).grid()
        
        buttonOption.set(0)
    
    def callFunction(self, master, monthsDict, transactionsList, inputYear, buttonOption): 
        ''' Call one of the three functions '''
        self._functionsList[buttonOption](master, monthsDict, transactionsList, inputYear)
    
    def allTransactions(self, master, monthsDict, transactionsList, inputYear):  
        # Fill 'monthsDict' for given 'inputYear'
        for record in transactionsList:
            if datetime.strptime(record[master._transactionDate], master._transactionDateFormat).year == inputYear:
                # Idea of following lines: monthsDict[month] += cost
                monthsDict[datetime.strptime(record[master._transactionDate], master._transactionDateFormat).strftime('%B')] += \
                float(record[master._transactionCost])
        
        listboxObj = TransactionsListbox(master, monthsDict, transactionsList, inputYear, 'allTransactions', None, None, None)
        graphObj = MonthGraph(master, monthsDict, inputYear, listboxObj)
        
        listboxObj.referenceGraphObj(graphObj)
        
        self.destroy()
        
    def filteredTransactionsPrompt(self, master, monthsDict, transactionsList, inputYear):
        filterList = []
        filteredTransObj = FilteredTransactionsPrompt(master, monthsDict, transactionsList, filterList, inputYear)
        self.destroy()
    
    def specificTransactionPrompt(self, master, monthsDict, transactionsList, inputYear):
        specificTransObj = SpecificTransactionsNamePrompt(master, monthsDict, transactionsList, inputYear)
        self.destroy()
    
class FilteredTransactionsPrompt(tk.Toplevel):
    def __init__(self, master, monthsDict, transactionsList, filterList, inputYear):
        super().__init__(master)    
        self.transient(master)     
        
        # Class variable
        removedRecords = []
        
        # Formatting
        self.minsize(300, 75)
        self.title("Prompt Window")
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)           
        
        # User prompt
        inputFilters = tk.StringVar()
        tk.Label(self, text= "Enter filters (separated by commas): ").grid()
        entryWidget = tk.Entry(self, textvariable=inputFilters)
        entryWidget.grid()  
        confirmButton = tk.Button(self, text= "Continue", command= lambda: self.callFunctionsAndWindows\
                                  (master, monthsDict, transactionsList, filterList, inputYear, removedRecords, inputFilters.get())).grid()  
    
    def callFunctionsAndWindows(self, master, monthsDict, transactionsList, filterList, inputYear, removedRecords, inputFilters):
        if inputFilters is "":
            tk.messagebox.showerror("Error", "Invalid input: Cannot be empty", parent=self)  
            
        else:
            self.parseFilters(filterList, inputFilters)
            self.fillMonthsDict(master, monthsDict, transactionsList, filterList, inputYear, inputFilters)
            
            # Creating windows
            listboxObj = TransactionsListbox(master, monthsDict, transactionsList, inputYear, 'filteredTransactions', filterList, removedRecords, None)
            graphObj = MonthGraph(master, monthsDict, inputYear, listboxObj)      
            removedTransObj = RemovedTransactions(master, monthsDict, transactionsList, inputYear, removedRecords, filterList, listboxObj, graphObj)
            
            listboxObj.referenceGraphObj(graphObj)
            listboxObj.referenceRemovedTransObj(removedTransObj)
            graphObj.referenceRemovedTransObj(removedTransObj)
            
            self.destroy()        
    
    def parseFilters(self, filterList, inputFilters):
        tempList = inputFilters.split(",")
        tempList = [name.lower().strip() for name in tempList if name.lower().strip() not in filterList] # Do not add filter if already in filterList
        tempSet = set(tempList) # Removes duplicate filters in the list (if typed twice during user input)
        filterList.extend(tempSet)
        
    def fillMonthsDict(self, master, monthsDict, transactionsList, filterList, inputYear, inputFilters):
        for record in transactionsList:
            try:
                if inputFilters is not "":
                    for name in filterList:
                        if name in record[master._transactionName].lower():
                                raise Exception
                            
                if datetime.strptime(record[master._transactionDate], master._transactionDateFormat).year == inputYear:
                    monthsDict[datetime.strptime(record[master._transactionDate], master._transactionDateFormat).strftime('%B')] += \
                    float(record[master._transactionCost])  
            except:
                continue             
                
class RemovedTransactions(tk.Toplevel):
    def __init__(self, master, monthsDict, transactionsList, inputYear, removedRecords, filterList, listboxObj, graphObj):
        super().__init__(master)
        self.transient(master)   
        
        self._total = 0
        self._newInputFilters = tk.StringVar() 
        
        # Formatting
        self.minsize(560, 750)
        for idx in range(0, 8):
            self.grid_rowconfigure(idx, weight=1)
        self.grid_columnconfigure(0, weight=1)           
        self.title("List of Removed Transactions")
        tk.Label(self, text = "Currently filtering: ").grid()
        tk.Label(self, text = ", ".join(filterList)).grid()
        
        self.createListbox(master, removedRecords)
        self.displayResultAnalysis()
        self.filterPrompt(master, monthsDict, transactionsList, inputYear, removedRecords, filterList, listboxObj, graphObj)
        
        self.protocol("WM_DELETE_WINDOW", lambda: self.exitWindows(listboxObj, graphObj))
        
    def createListbox(self, master, removedRecords):
        scrollbar = tk.Scrollbar(self)
        scrollbar.grid(row=2, column=1, sticky="ns")
        listbox = tk.Listbox(self, height=50, width=75, selectmode="extended", yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        listbox.grid(row=2, column=0)         
        
        for record in removedRecords: # Fill listbox with data from removedRecords     
            self._total += float(record[master._transactionCost])
            listbox.insert(tk.END, "{:16}".format((datetime.strptime(record[master._transactionDate], master._transactionDateFormat)).strftime('%m/%d/%Y')) 
                                 + "{:18}".format(str(" $" + record[master._transactionCost])) + record[master._transactionName])          
    
    def displayResultAnalysis(self):
        tk.Label(self, text= str("Total: $" + "{0:.2f}".format(self._total))).grid()  
        
    def filterPrompt(self, master, monthsDict, transactionsList, inputYear, removedRecords, filterList, listboxObj, graphObj):       
        ''' Calls displayFilteredTransactions() '''
        tk.Label(self).grid()
        tk.Label(self, text= "Enter additional filters (separated by commas),").grid()
        tk.Label(self, text= "or enter an empty input to clear filters:").grid()
        entryWidget = tk.Entry(self, textvariable= self._newInputFilters)
        entryWidget.grid()
        entryWidget.bind("<Return>", lambda event: \
                         self.updateFilteredTransactions(master, monthsDict, transactionsList, inputYear, removedRecords, filterList, listboxObj, graphObj))    
        
    def updateFilteredTransactions(self, master, monthsDict, transactionsList, inputYear, removedRecords, filterList, listboxObj, graphObj):       
        ''' Close all windows, reset variables after adding new filters, and create new windows '''
        listboxObj.destroy()
        graphObj.destroy()
        
        # Reset necessary variables
        removedRecords.clear()
        monthsDict = dict.fromkeys(monthsDict, 0.0)
        
        self.parseFilters(filterList, self._newInputFilters.get())
        self.fillMonthsDict(master, monthsDict, transactionsList, filterList, inputYear, self._newInputFilters.get())
        
        # Creating windows
        newListboxObj = TransactionsListbox\
            (master, monthsDict, transactionsList, inputYear, 'filteredTransactions', filterList, removedRecords, None)
        newGraphObj = MonthGraph(master, monthsDict, inputYear, newListboxObj) 
        newRemovedTransObj = RemovedTransactions\
            (master, monthsDict, transactionsList, inputYear, removedRecords, filterList, newListboxObj, newGraphObj)
        
        newListboxObj.referenceGraphObj(newGraphObj)
        newListboxObj.referenceRemovedTransObj(newRemovedTransObj)
        newGraphObj.referenceRemovedTransObj(newRemovedTransObj)
            
        self.destroy()       
    
    def parseFilters(self, filterList, inputFilters):
        tempList = inputFilters.split(",")
        tempList = [name.lower().strip() for name in tempList if name.lower().strip() not in filterList] # Do not add filter if already in filterList
        tempSet = set(tempList) # Removes duplicate filters in the list (if typed twice during user input)
        filterList.extend(tempSet)    
        
    def fillMonthsDict(self, master, monthsDict, transactionsList, filterList, inputYear, inputFilters):
        for record in transactionsList:
            try:
                if inputFilters is not "":
                    for name in filterList:
                        if name in record[master._transactionName].lower():
                                raise Exception
                              
                    if datetime.strptime(record[master._transactionDate], master._transactionDateFormat).year == inputYear:
                        monthsDict[datetime.strptime(record[master._transactionDate], master._transactionDateFormat).strftime('%B')] += \
                        float(record[master._transactionCost])
                        
                # Empty input means clearing 'filterList'
                else:
                    filterList.clear()
                    
                    if datetime.strptime(record[master._transactionDate], master._transactionDateFormat).year == inputYear:
                        monthsDict[datetime.strptime(record[master._transactionDate], master._transactionDateFormat).strftime('%B')] += \
                        float(record[master._transactionCost])                     
            except:
                continue   
            
    def exitWindows(self, listboxObj, graphObj):
        listboxObj.destroy()
        graphObj.destroy()
        self.destroy()          
            
class SpecificTransactionsNamePrompt(tk.Toplevel):
    def __init__(self, master, monthsDict, transactionsList, inputYear):
        super().__init__(master)    
        self.transient(master)   
        
        # Formatting
        self.minsize(350, 75)
        self.title("Prompt Window")
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)        
        
        # User prompt for specific name of transaction
        inputNames = tk.StringVar()
        tk.Label(self, text= "Enter transaction names (separated by commas):").grid()
        entryWidget = tk.Entry(self, textvariable= inputNames)
        entryWidget.grid()  
        confirmButton = tk.Button(self, text= "Continue", command= lambda: \
                                  self.callWindows(master, monthsDict, transactionsList, inputYear, inputNames.get())).grid() 
        
    def callWindows(self, master, monthsDict, transactionsList, inputYear, inputNames):
        namesList = []
        self.parseFilters(inputNames, namesList)

        # Fill 'monthDict' for given 'inputYear' and 'namesList'
        for record in transactionsList:
            if datetime.strptime(record[master._transactionDate], master._transactionDateFormat).year == inputYear:
                for name in namesList:
                    if name in record[master._transactionName].lower():
                        monthsDict[datetime.strptime(record[master._transactionDate], master._transactionDateFormat).strftime('%B')] += \
                        float(record[master._transactionCost])
                        break
        
        listboxObj = TransactionsListbox(master, monthsDict, transactionsList, inputYear, 'specificTransaction', None, None, namesList)
        graphObj = MonthGraph(master, monthsDict, inputYear, listboxObj)
        
        listboxObj.referenceGraphObj(graphObj)
        
        self.destroy()          
        
    def parseFilters(self, inputNames, namesList):
        tempList = inputNames.split(",")
        tempList = [name.lower().strip() for name in tempList if name.lower().strip() not in namesList] # Do not add filter if already in namesList
        tempSet = set(tempList) # Removes duplicate filters in the list (if typed twice during user input)
        namesList.extend(tempSet)    

class TransactionsListbox(tk.Toplevel):
    ''' A listbox for all three options '''
    def __init__(self, master, monthsDict, transactionsList, inputYear, userTransactionOption, filterList, removedRecords, namesList):
        super().__init__(master)    
        self.transient(master)         
        
        # Class variables for references
        self._graphObj = None
        self._removedTransObj = None
        self._monthsValueCount = len(list(filter(lambda value: value > 0, monthsDict.values()))) # This counts non-zero values in monthsDict
        
        # Formatting
        self.minsize(560, 750)
        for idx in range(0, (6 + self._monthsValueCount)):
            self.grid_rowconfigure(idx, weight=1)
        self.grid_columnconfigure(0, weight=1)         
        self.title("List of Transactions")
        tk.Label(self, text = "Displaying transactions").grid() # grid(0,0)          
        
        self.createListbox(master, transactionsList, inputYear, userTransactionOption, filterList, removedRecords, namesList)
        self.displayResultAnalysis(monthsDict)
        
        self.protocol("WM_DELETE_WINDOW", self.exitWindows)
        
    def createListbox(self, master, transactionsList, inputYear, userTransactionOption, filterList, removedRecords, namesList):
        # Display filters for 'specificTransactions' listbox
        rowNumber = 1
        
        if userTransactionOption == 'specificTransaction':
            tk.Label(self).grid()
            tk.Label(self, text = str("Currently filtering: " + str(", ".join(namesList)))).grid()   
            rowNumber = 3
        
        scrollbar = tk.Scrollbar(self)
        scrollbar.grid(row=rowNumber, column=1, sticky="ns")
        listbox = tk.Listbox(self, height=50, width=75, selectmode="extended", yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        listbox.grid(row=rowNumber, column = 0)       
        
        if userTransactionOption == 'allTransactions':
            for record in transactionsList:      
                if datetime.strptime(record[master._transactionDate], master._transactionDateFormat).year == inputYear:
                    listbox.insert(tk.END, "{:16}".format((datetime.strptime(record[master._transactionDate], master._transactionDateFormat)).strftime('%m/%d/%Y')) 
                                         + "{:18}".format(str(" $" + record[master._transactionCost])) + record[master._transactionName]) 
        elif userTransactionOption == 'filteredTransactions':
            for record in transactionsList: # Fill listbox with all transactions within 'transactionsList'
                try:
                    if datetime.strptime(record[master._transactionDate], master._transactionDateFormat).year == inputYear:
                        for name in filterList:
                            if name in record[master._transactionName].lower():
                                removedRecords.append(record)
                                raise Exception
                                
                        listbox.insert(tk.END, "{:16}".format((datetime.strptime(record[master._transactionDate], master._transactionDateFormat)).strftime('%m/%d/%Y')) 
                                             + "{:18}".format(str(" $" + record[master._transactionCost])) + record[master._transactionName])  
                except:
                    continue       
        elif userTransactionOption == 'specificTransaction':
            for record in transactionsList:  
                if datetime.strptime(record[master._transactionDate], master._transactionDateFormat).year == inputYear:
                    for name in namesList:
                        if name in record[master._transactionName].lower():
                            listbox.insert(tk.END, "{:16}".format(\
                                (datetime.strptime(record[master._transactionDate], master._transactionDateFormat)).strftime('%m/%d/%Y')) 
                                           + "{:18}".format(str(" $" + record[master._transactionCost])) + record[master._transactionName])
                            break
            
    def displayResultAnalysis(self, monthsDict):
        tk.Label(self, text= str("Average per month:" + " $" + "{0:.2f}".format(sum(monthsDict.values()) / self._monthsValueCount))).grid()
        tk.Label(self).grid()
        
        for month,cost in monthsDict.items():
            if cost != 0:
                tk.Label(self, text= str(month + ": $" + "{0:.2f}".format(cost))).grid()   
                
    def referenceGraphObj(self, graphObj):
        self._graphObj = graphObj
        
    def referenceRemovedTransObj(self, removedTransObj):
        self._removedTransObj = removedTransObj        
        
    def exitWindows(self):
        self._graphObj.destroy()
        if self._removedTransObj is not None:
            self._removedTransObj.destroy()
        self.destroy()    
        
class MonthGraph(tk.Toplevel):
    def __init__(self, master, monthsDict, inputYear, listboxObj):
        super().__init__(master)    
        self.transient(master)
        
        self._removedTransObj = None
        
        fig = plt.figure(figsize=(13, 9))
        self.title("Monthly Expenses for the Year: " + str(inputYear))
        plt.title(str("Total: $" + "{0:.2f}".format(sum(monthsDict.values()))))

        plt.bar([month for month,cost in monthsDict.items() if cost != 0], \
                [cost for cost in monthsDict.values() if cost != 0], align="center")
        
        plt.xlabel("Months")
        plt.ylabel("In Dollars")
        
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        canvas.draw()      
        
        self.protocol("WM_DELETE_WINDOW", lambda: self.exitWindows(listboxObj))
        
    def referenceRemovedTransObj(self, removedTransObj):
        self._removedTransObj = removedTransObj
        
    def exitWindows(self, listboxObj):
        listboxObj.destroy()
        if self._removedTransObj is not None:
            self._removedTransObj.destroy()
        self.destroy()
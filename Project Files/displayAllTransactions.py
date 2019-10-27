# Johnny Nguyen
# displayAllTransactions class

import matplotlib
matplotlib.use('TkAgg') # Tell matplotlib to work with Tkinter
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Tells matplotlib about Canvas object
import matplotlib.pyplot as plt 
from datetime import datetime

class TransactionOptions(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.transient(master)  
        
        # Formatting
        self.minsize(225, 175)
        for idx in range(0, 3):
            self.grid_rowconfigure(idx, weight=1)
        self.grid_columnconfigure(0, weight=1)          
        self.title("Displaying Transaction Options")
        
        tk.Button(self, text= "Sorted by date", command= lambda: self.transactionListByDate(master)).grid()
        tk.Button(self, text= "Sorted by name", command= lambda: self.transactionsListByName(master)).grid()
        tk.Button(self, text= "Sorted by cost", command= lambda: self.transactionsListByCost(master)).grid()   
        
    def transactionListByDate(self, master):
        ''' Uses the master's transactions list, which is sorted by date by default '''
        AllTransactions(master, master._transactionsList)
        self.destroy()
        
    def transactionsListByName(self, master):
        ''' Resort the master's transactions list into a new list by name'''
        transactionsList = sorted(master._transactionsList, key= lambda record: record[master._transactionName])
        sortedByNameObj = AllTransactions(master, transactionsList)
        self.destroy()
        
    def transactionsListByCost(self, master):
        ''' Resort the master's transactions list into a new list by cost'''
        transactionsList = sorted(master._transactionsList, key= lambda record: float(record[master._transactionCost].strip()), reverse=True)
        sortedByCostObj = AllTransactions(master, transactionsList)
        self.destroy()
        
class AllTransactions(tk.Toplevel):
    def __init__(self, master, transactionsList):
        super().__init__(master)
        self.transient(master)         
        
        # Class variables
        self._total = 0
        self._transactionsCount = 0
        self._newInputFilters = tk.StringVar()    
        
        # Formatting
        self.minsize(560, 750)
        for idx in range(0, 8):
            self.grid_rowconfigure(idx, weight=1)
        self.grid_columnconfigure(0, weight=1)         
        self.title("Displaying All Transactions")
        tk.Label(self, text = "Analysis of all transactions").grid() # grid(0,0)         
        
        # Functions
        self.createListbox(master, transactionsList)
        self.displayResultAnalysis()
        self.filterPrompt(master, transactionsList)
    
    def createListbox(self, master, transactionsList):    
        scrollbar = tk.Scrollbar(self)
        scrollbar.grid(row=1, column=1, sticky="ns")
        listbox = tk.Listbox(self, height=50, width=75, selectmode="extended", yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        listbox.grid(row = 1, column = 0)       
        
        for record in transactionsList: # Fill listbox with all transactions within 'transactionsList'
            self._total += float(record[master._transactionCost].strip())
            self._transactionsCount += 1              
            listbox.insert(tk.END, "{:16}".format((datetime.strptime(record[master._transactionDate], master._transactionDateFormat)).strftime('%m/%d/%Y')) 
                                 + "{:18}".format(str(" $" + record[master._transactionCost])) + record[master._transactionName])  
            
    def displayResultAnalysis(self):
        tk.Label(self, text= str("Total: $" + "{0:.2f}".format(self._total))).grid()
        tk.Label(self, text= str("Number of transactions: " + str(self._transactionsCount))).grid()
        tk.Label(self).grid()     
        
    def filterPrompt(self, master, transactionsList):       
        ''' Calls displayFilteredTransactions() '''
        tk.Label(self, text= "Enter any transaction name to filter out (separated by commas),").grid()
        tk.Label(self, text= "or enter an empty input to clear filters:").grid()
        entryWidget = tk.Entry(self, textvariable= self._newInputFilters)
        entryWidget.grid()
        entryWidget.bind("<Return>", lambda event: self.displayFilteredTransactions(master, transactionsList))          
    
    def displayFilteredTransactions(self, master, transactionsList):
        if self._newInputFilters.get() is "":
            allTransObj = AllTransactions(master, transactionsList)
        else:
            filtersList = []
            filteredTransObj = FilteredTransactions(master, transactionsList, self._newInputFilters.get(), filtersList)
            
        self.destroy()
        
class FilteredTransactions(tk.Toplevel):
    def __init__(self, master, transactionsList, inputFilters, filtersList):
        super().__init__(master)
        self.transient(master) 
        
        # Class variables
        self._total = 0
        self._transactionsCount = 0        
        self._removedRecords = []
        self._newInputFilters = tk.StringVar()
        
        # Class variables for references
        self._graphObj = None        
        
        # Formatting
        self.minsize(560, 750)
        for idx in range(0, 8):
            self.grid_rowconfigure(idx, weight=1)
        self.grid_columnconfigure(0, weight=1)          
        self.title("Displaying Filtered Transactions")
        tk.Label(self, text= "Analysis of filtered transactions").grid() # grid(0,0) 

        # Functions
        self.parseFilters(inputFilters, filtersList)
        self.createListbox(master, transactionsList, inputFilters, filtersList)
        self.displayResultAnalysis()
        self.filterPrompt(master, transactionsList, filtersList)     
        
        # Call a separate window to display removed transactions
        self._removedTransObj = RemovedTransactions(master, filtersList, self._removedRecords, self)   
        
        self.protocol("WM_DELETE_WINDOW", self.exitWindows)
    
    def parseFilters(self, inputFilters, filtersList):
        tempList = inputFilters.split(",")
        tempList = [name.lower().strip() for name in tempList if name.lower().strip() not in filtersList] # Do not add filter if already in filtersList
        tempSet = set(tempList) # Removes duplicate filters in the list (if typed twice during user input)
        filtersList.extend(tempSet)        
    
    def createListbox(self, master, transactionsList, inputFilters, filtersList):
        scrollbar = tk.Scrollbar(self)
        scrollbar.grid(row=1, column=1, sticky="ns")
        listbox = tk.Listbox(self, height=50, width=75, selectmode="extended", yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        listbox.grid(row=1, column=0)         
        
        for record in transactionsList: # Fill listbox with all transactions within 'transactionsList'
            try:
                if inputFilters is not "":
                    for name in filtersList:
                        if name in record[master._transactionName].lower():
                                self._removedRecords.append(record)
                                raise Exception
                
                self._total += float(record[master._transactionCost])
                self._transactionsCount += 1              
                listbox.insert(tk.END, "{:16}".format((datetime.strptime(record[master._transactionDate], master._transactionDateFormat)).strftime('%m/%d/%Y')) 
                                 + "{:18}".format(str(" $" + record[master._transactionCost])) + record[master._transactionName])  
            except:
                continue        
            
    def displayResultAnalysis(self):
        tk.Label(self, text= str("Total: $" + "{0:.2f}".format(self._total))).grid()
        tk.Label(self, text= str("Number of transactions: " + str(self._transactionsCount))).grid()  
        tk.Label(self).grid()       
        
    def filterPrompt(self, master, transactionsList, filtersList):
        ''' Calls displayFilteredTransactions() '''
        tk.Label(self, text= "Enter any transaction name to remove (separated by commas),").grid()
        tk.Label(self, text= "or enter an empty input to clear filters:").grid()
        entryWidget = tk.Entry(self, textvariable= self._newInputFilters)
        entryWidget.grid()
        entryWidget.bind("<Return>", lambda event: self.displayFilteredTransactions(master, transactionsList, filtersList))          
        
    def displayFilteredTransactions(self, master, transactionsList, filtersList):        
        if self._newInputFilters.get() is "":
            allTransObj = AllTransactions(master, transactionsList)
        else:
            filteredTransObj = FilteredTransactions(master, transactionsList, self._newInputFilters.get(), filtersList)   
            
        self.destroy()
        self._removedTransObj.destroy()    
        if self._graphObj is not None:
            self._graphObj.destroy()        
        
    def referenceGraphObj(self, graphObj):
        self._graphObj = graphObj    
        
    def exitWindows(self):
        self._removedTransObj.destroy()
        self.destroy()
        if self._graphObj is not None:
            self._graphObj.destroy()
        
class RemovedTransactions(tk.Toplevel):
    def __init__(self, master, filtersList, removedRecords, filteredTransObj):
        super().__init__(master)
        self.transient(master) 
        
        # Class variables
        self._total = 0
        self._transactionsCount = 0         
        filtersDict = {}
        for name in filtersList:
            filtersDict[name] = {'total': 0.0, 'count': 0}       
            
        # Class variables for references
        self._graphObj = None                
        
        # Formatting
        for idx in range(0, (7 + (3 * len(filtersList)))):
            self.grid_rowconfigure(idx, weight=1)
        self.grid_columnconfigure(0, weight=1)          
        self.title("Displaying Removed Records")
        tk.Label(self, text= "Currently filtering: ").grid()
        tk.Label(self, text= ", ".join(filtersList)).grid()
        
        self.createListbox(master, removedRecords, filtersList, filtersDict)
        self.displayResultAnalysis(filtersList, filtersDict)
            
        tk.Button(self, text= "Display graph", 
                  command= lambda: RemovedTransactionsGraph(master, filtersDict, self._total, filteredTransObj, self)).grid()
        
        self.protocol("WM_DELETE_WINDOW", lambda: self.exitWindows(filteredTransObj))
        
    def createListbox(self, master, removedRecords, filtersList, filtersDict):
        scrollbar = tk.Scrollbar(self)
        scrollbar.grid(row=2, column=1, sticky="ns")
        listbox = tk.Listbox(self, height=50, width=75, selectmode="extended", yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        listbox.grid(row=2, column=0)         
        
        for record in removedRecords: # Fill listbox with data from removedRecords
            for name in filtersList:
                if name in record[master._transactionName].lower():
                    filtersDict[name]['total'] += float(record[master._transactionCost])
                    filtersDict[name]['count'] += 1
            
            self._total += float(record[master._transactionCost].strip())
            self._transactionsCount += 1              
            listbox.insert(tk.END, "{:16}".format((datetime.strptime(record[master._transactionDate], master._transactionDateFormat)).strftime('%m/%d/%Y')) 
                                 + "{:18}".format(str(" $" + record[master._transactionCost])) + record[master._transactionName])          
        
    def displayResultAnalysis(self, filtersList, filtersDict):
        tk.Label(self, text= str("Total: $" + "{0:.2f}".format(self._total))).grid()
        tk.Label(self, text= str("Number of transactions: " + str(self._transactionsCount))).grid() 
        
        for name in filtersList:
            tk.Label(self).grid() 
            tk.Label(self, text= str("Total for \'" + name + "\': $" + "{0:.2f}".format(filtersDict[name]['total']))).grid()
            tk.Label(self, text= str("Number of transactions: " + str(filtersDict[name]['count']))).grid() 
        
        tk.Label(self).grid() 
        
    def referenceGraphObj(self, graphObj):
        self._graphObj = graphObj         
        
    def exitWindows(self, filteredTransObj):
        filteredTransObj.destroy()
        if self._graphObj is not None:
            self._graphObj.destroy()        
        self.destroy()    
        
class RemovedTransactionsGraph(tk.Toplevel):
    def __init__(self, master, filtersDict, total, filteredTransObj, removedTransObj):
        super().__init__(master)    
        self.transient(master)
        
        filteredTransObj.referenceGraphObj(self)
        removedTransObj.referenceGraphObj(self)
        
        fig = plt.figure()
        self.title("Visual Representation of Filters")
        plt.title(str("Total: $" + "{0:.2f}".format(total)))
        
        sortedFiltersList = sorted(filtersDict.items(), key=lambda k: k[1]['total'], reverse=True) # The [1] points to the dictionary's value
        
        # In sortedFiltersList, item[0] points to the name and item[1] points to the value
        plt.bar([str("\'" + item[0] + "\'") for item in sortedFiltersList], [item[1]['total'] for item in sortedFiltersList])
        
        plt.xlabel("Filters")
        plt.ylabel("In Dollars")
        
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        canvas.draw()         
        
        self.protocol("WM_DELETE_WINDOW", lambda: self.exitWindows(filteredTransObj, removedTransObj))
        
    def exitWindows(self, filteredTransObj, removedTransObj):
        filteredTransObj.destroy()
        removedTransObj.destroy()
        self.destroy()      
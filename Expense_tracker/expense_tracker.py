# Build a program to showcase pure python skills
"""
-Build a personal finance tracker app, using json to store data.
Users will add dates and expenses and receive analysis and be able to view them over time. 
"""

import datetime

welcome_message = "Hi and welcome to the Personal Finance Tracker App"
line_break = "*" * 50

def expense_func():
	print(line_break,"\n",line_break, "\n",line_break)
	print(welcome_message)
	
	expense_info = []
	category = input("What kind of expense would you like to track today? \n Food, Gas, Grocery, Utility, Rent, etc...")
	amount = int(input("How much is the {expense_type} cost? Enter a number. "))
	date = datetime.date(input("What day did you make this expense? MM-DD-YYYY"))
	description = input("Give a quick description of the expense.. ")
	
	expense_info = {var: locals()[var] for var in expense_info}
	
	
	return expense_info	
#	print(f"Ofcourse! We will track your {user_response} expense today.")
	
	
if __name__ == "__main__":
	expense_func()


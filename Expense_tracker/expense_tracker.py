# Build a program to showcase pure python skills
"""
-Build a personal finance tracker app, using json to store data.
Users will add dates and expenses and receive analysis and be able to view them over time. 
"""

from datetime import datetime 
import json
from io import StringIO
import time

welcome_message = "Hi and welcome to the Personal Finance Tracker App"
line_break = "*" * 50

def expense_func():
	"""
	Ask user for expense information and return a dictionary of the expense information
	"""

	print(line_break,"\n",line_break, "\n",line_break)
	print(welcome_message)
	
	expense_info = []
	category = input("What kind of expense would you like to track today? \n Food, Gas, Grocery, Utility, Rent, etc...")
	amount = int(input(f"How much is the {category} cost? Enter a number. "))
	date_str = input("What day did you make this expense? MMDDYYYY ->")
	date = datetime.strptime(date_str, "%m%d%Y")
	description = input("Give a quick description of the expense.. ")
	
	expense_info.extend([category, amount, date, description])
	expense_dict = {k: v for k,v in locals().items() if k in ['category', 'amount', 'date', 'description']}

	print(line_break)
	print("Here is the expense you entered: ", expense_dict)

	unique_id = f"expense_{int(time.time())}"
	
	return expense_dict, unique_id

def save_as_json(exp_dict, unique_id):
	"""
	Save the expense information as a json file
	"""
	global io
	
	io = StringIO()
	
	io.seek(0)
	try:
		existing_data = json.load(io)
	except json.decoder.JSONDecodeError:
		existing_data = []

	existing_data.append(exp_dict)
	json.dump(exp_dict, io)
	io.seek(0)

	return io



def table_of_expenses(exp_dict):
	"""
	Show a table of expenses
	"""
	print("Here is a table of your expenses")
	print(f"{'Date':<10} {'Category':<10} {'Amount':<10} {'Description':<20}")
	print(line_break)

	for exp in exp_dict:
		print(f"{exp['date']:<10} {exp['category']:<10} {exp['amount']:<10} {exp['description']:<20}")

	
	
if __name__ == "__main__":
	expense_dict, unique_id = expense_func()
	io = save_as_json(expense_dict, unique_id)

	for line in io:
		print(line)

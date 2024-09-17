# Build a program to showcase pure python skills
"""
-Build a personal finance tracker app, using json to store data.
Users will add dates and expenses and receive analysis and be able to view them over time. 
"""

from datetime import datetime 
import json
from io import StringIO
import time
import re

welcome_message = "Hi and welcome to the Personal Finance Tracker App"
line_break = "*" * 50


def expense_func():
	"""
	Ask user for expense information and return a dictionary of the expense information
	"""

	print(line_break,"\n",line_break, "\n",line_break)
	print(welcome_message)
	
	expense_info = []
	# Validate category input
	category = input("What kind of expense would you like to track today? \n Food, Gas, Grocery, Utility, Rent, etc...")
	while True:
		try:
			amount = float(input(f"How much is the {category} cost? Enter a number. "))
			break
		except ValueError:
			print("Invalid input. Please enter a number.")
	# Validate date input
	while True:	
		try:
			date_str = input("What day did you make this expense? MMDDYYYY ->")
			match = re.match(r"(\d{2})(\d{2})(\d{4})", date_str)
			if not match:
				raise ValueError("Invalid date format.")
			date = datetime.strptime(date_str, "%m%d%Y").date().isoformat()
			break
		except ValueError as e:
			print(f"Error: {e} Please use MMDDYYYY formatting!")

	description = input("Give a quick description of the expense.. ")
	
	expense_info.extend([category, amount, date, description])
	expense_dict = {k: v for k,v in locals().items() if k in ['category', 'amount', 'date', 'description']}

	print(line_break)
	print("Here is the expense you entered: ", expense_dict)

	unique_id = f"expense_{int(time.time())}"
	
	return expense_dict, unique_id


def save_as_json(exp_dict, unique_id):
	"""
	Save the expense information as a json file to a StringIO buffer.
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


def table_of_expenses(io):
	"""
	Show a table of expenses
	"""
	print("Here is a table of your expenses")
	print(f"\n{'Date':<16} {'Category':<10} {'Amount':<10} {'Description':<10}")
	print(line_break)

	de_io = json.loads(io.readlines()[0])
	print(f"{de_io['date']:<16} {de_io['category']:<10} {de_io['amount']:<10} {de_io['description']:<10}")

		

	
	
if __name__ == "__main__":
	expense_dict, unique_id = expense_func()
	io = save_as_json(expense_dict, unique_id)

	table_of_expenses(io)


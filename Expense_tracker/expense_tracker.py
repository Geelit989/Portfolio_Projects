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
			if amount <= 0:
				raise ValueError("Please enter a positive number.")
			break
		except ValueError as e:
			print("Invalid Input!: ", e)
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
	expense_dict = {
		'category': category,
		'amount': amount,
		'date': date,
		'description': description,
	}

	print(line_break)
	print("Here is the expense you entered: ", expense_dict)

	unique_id = f"expense_{int(time.time())}"
	
	return expense_dict, unique_id


def file_save(exp_dict, unique_id):
	"""
	Save the expense information as a json file to a StringIO buffer.
	"""
	try:
		exp_dict['id'] = unique_id
		with open('expenses.json', 'r+') as f:
			existing_data = json.load(f)
	except (json.JSONDecodeError, FileNotFoundError) as e:
		existing_data = []
	
	exp_dict['id'] = unique_id
	existing_data.append(exp_dict)

	with open('expenses.json', 'w') as f:
		json.dump(existing_data, f, indent=4)


def table_of_expenses(file='expenses.json'):
	"""
	Show a table of expenses
	"""
	print("Here is a table of your expenses")
	print(f"\n{'Date':<16} {'Category':<10} {'Amount':<10} {'Description':<10}")
	print(line_break)

	with open(file, 'r') as f:
		expenses = json.load(f)
		for exp in expenses:
			print(f"{exp['date']:<16} {exp['category']:<10} {exp['amount']:<10} {exp['description']:<10}")

	
if __name__ == "__main__":
	expense_dict, unique_id = expense_func()
	file_save(expense_dict, unique_id)

	with open('expenses.json','r') as f:
		print("This is from Expense.json file")
		print(f.read())

	table_of_expenses()


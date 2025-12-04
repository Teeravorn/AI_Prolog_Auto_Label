import os
import pandas as pd
import re
from pyswip import Prolog
from lib.auto_label.query_engine_config import (
	load_config,
	build_column_mapping,
	get_label_column,
	get_multi_label_mode,
	get_csv_headers,
	get_rules_file
)

def extract_predicates_from_rules(rule_file):
	"""
	Extract predicates from Prolog rule file.
	
	Args:
		rule_file (str): Path to the .pl rule file
		
	Returns:
		tuple: (label_predicates list, all_rules list)
			- label_predicates: predicates that output labels
			- all_rules: all rules as text for chain rule support
	"""
	label_predicates = []
	all_rules = []
	
	with open(rule_file, 'r', encoding='utf-8') as f:
		for line in f:
			line = line.strip()
			if not line or line.startswith('%'):
				continue
			
			all_rules.append(line)
			
			# Pattern: label_name(Arguments, 'Label') :- condition.
			# These are the final labeling predicates
			match = re.search(r"(\w+)\((.+),\s*'([^']+)'\)\s*:-", line)
			if match:
				args_str = match.group(2).strip()
				# Parse individual argument names (variable names)
				# Split by comma and extract variable names
				arg_list = [a.strip() for a in args_str.split(',')]
				
				# Keep ALL arguments including underscores
				# Map each argument to its Prolog variable name or underscore
				label_predicates.append({
					'name': match.group(1),
					'args': args_str,
					'arg_names': arg_list,  # All arguments including _
					'arg_count': len(arg_list),
					'type': 'label_predicate',
					'has_label': True
				})
	
	print(f"Detected {len(label_predicates)} label predicates and {len(all_rules)} total rules")
	print("Label predicates:")
	for p in label_predicates:
		print(f"  - {p['name']} ({p.get('arg_count', 0)} args): {p.get('args', '')}")
	
	return label_predicates, all_rules

def get_row_values(row, column_mapping):
	"""
	Extract row values based on column mapping.
	
	Args:
		row (pd.Series): DataFrame row
		column_mapping (dict): Mapping from Prolog variable names to CSV columns
		
	Returns:
		dict: Dictionary of {prolog_name: value}
	"""
	row_values = {}
	if column_mapping:
		for prolog_name, csv_col in column_mapping.items():
			value = row.get(csv_col, 0)
			
			# Convert time format "HH:MM" to hour integer
			if isinstance(value, str) and ':' in value:
				try:
					hour = int(value.split(':')[0])
					row_values[prolog_name] = hour
				except:
					row_values[prolog_name] = value
			else:
				row_values[prolog_name] = value
	return row_values

def assert_prolog_facts(prolog, row_values):
	"""
	Assert facts for current row in Prolog.
	
	Args:
		prolog (Prolog): PySwip Prolog instance
		row_values (dict): Dictionary of {prolog_name: value}
	"""
	for prolog_name, value in row_values.items():
		prolog.assertz(f"{prolog_name.lower()}({value})")

def retract_prolog_facts(prolog, row_values):
	"""
	Retract facts for current row from Prolog.
	
	Args:
		prolog (Prolog): PySwip Prolog instance
		row_values (dict): Dictionary of {prolog_name: value}
	"""
	for prolog_name, value in row_values.items():
		try:
			prolog.retract(f"{prolog_name.lower()}({value})")
		except:
			pass

def build_query_string(pred, row_values, prolog_var_names):
	"""
	Build Prolog query string based on predicate's actual arguments.
	
	Args:
		pred (dict): Predicate dictionary with 'arg_names' field
		row_values (dict): Dictionary of {prolog_name: value}
		prolog_var_names (list): List of all Prolog variable names in config
		
	Returns:
		str: Query string to execute
	"""
	# Use actual argument names from the rule
	arg_names = pred.get('arg_names', [])
	
	if not arg_names:
		# Fallback: use first variable
		if prolog_var_names:
			value = row_values.get(prolog_var_names[0], 0)
			return f"{pred['name']}({value}, Label)"
		return f"{pred['name']}(Label)"
	
	# Build query with values matching the rule's argument order
	var_values = []
	for var_name in arg_names:
		if var_name == '_':
			# For underscore, use Prolog anonymous variable
			var_values.append('_')
		else:
			# For named variables, get value from row
			value = row_values.get(var_name, 0)
			var_values.append(str(value))
	
	# Build query with actual arguments plus Label
	args_str = ', '.join(var_values)
	return f"{pred['name']}({args_str}, Label)"

def query_predicate(prolog, pred, row_values, prolog_var_names, multi_label, idx):
	"""
	Query a single predicate and collect matching labels.
	Supports chain rules through Prolog's inference engine.
	
	Args:
		prolog (Prolog): PySwip Prolog instance (with all rules loaded)
		pred (dict): Predicate dictionary
		row_values (dict): Dictionary of {prolog_name: value}
		prolog_var_names (list): List of Prolog variable names
		multi_label (bool): Whether to collect multiple labels
		idx (int): Row index for debugging
		
	Returns:
		list: List of matched labels
	"""
	matched_labels = []
	
	try:
		# Build and execute query - Prolog will handle chain rules automatically
		query_str = build_query_string(pred, row_values, prolog_var_names)
		
		if idx < 3:
			print(f"Querying: {query_str}")
		
		# Prolog engine will follow chain rules to find answers
		query_results = list(prolog.query(query_str))
		
		if idx < 3 and query_results:
			print(f"Results: {query_results}")
		
		# Collect all matching labels from this query
		for result in query_results:
			lbl = result.get('Label', '')
			if lbl and lbl not in matched_labels:
				matched_labels.append(lbl)
				if not multi_label:
					break  # Single label mode - stop at first match
				
	except Exception as e:
		if idx < 3:
			print(f"Error querying {pred['name']}: {e}")
	
	return matched_labels

def label_single_row(prolog, row, idx, predicates, column_mapping, prolog_var_names, multi_label):
	"""
	Label a single row by querying all predicates.
	
	Args:
		prolog (Prolog): PySwip Prolog instance
		row (pd.Series): DataFrame row
		idx (int): Row index
		predicates (list): List of predicate dictionaries
		column_mapping (dict): Mapping from Prolog variable names to CSV columns
		prolog_var_names (list): List of Prolog variable names
		multi_label (bool): Whether to collect multiple labels
		
	Returns:
		str: Final label(s) for the row
	"""
	matched_labels = []
	
	# Get values from row using config mapping
	row_values = get_row_values(row, column_mapping)
	
	if idx < 3:  # Debug first 3 rows
		print(f"\n=== Row {idx+1}: {row_values} ===")
	
	# Assert facts for current row
	assert_prolog_facts(prolog, row_values)
	
	# Query predicates
	for pred in predicates:
		pred_labels = query_predicate(prolog, pred, row_values, prolog_var_names, multi_label, idx)
		
		for lbl in pred_labels:
			if lbl not in matched_labels:
				matched_labels.append(lbl)
				if not multi_label:
					break  # Single label mode - stop at first match
		
		# If single label mode and we found a label, stop checking other predicates
		if not multi_label and matched_labels:
			break
	
	# Retract facts after processing row
	retract_prolog_facts(prolog, row_values)
	
	# Format label output
	if multi_label:
		return "; ".join(matched_labels) if matched_labels else ""
	else:
		return matched_labels[0] if matched_labels else ""


def apply_rule_to_csv(use_case, csv_path, kb_dir="KB", label_column=None, multi_label=None, rules_file=None):
	"""
	Apply rules to a CSV file and add a new label column using Prolog.
	
	Args:
		use_case (str): The use case name (e.g., 'PM_Temperature', 'useCase2').
		csv_path (str): Path to the CSV file to label.
		kb_dir (str): Directory where knowledge base files are stored.
		label_column (str): Name of the new label column to add (overrides config).
		multi_label (bool): If True, collect all matching labels (overrides config).
		rules_file (str): Specific rules filename to use (optional).
		
	Returns:
		pd.DataFrame: DataFrame with new label column.
	"""
	# Load config
	config = load_config(use_case, kb_dir)
	
	# Use config defaults if not specified
	if label_column is None:
		label_column = get_label_column(config)
	
	if multi_label is None:
		multi_label = get_multi_label_mode(config)
	
	# Load rule file - use specific file if provided, otherwise use config default
	if rules_file:
		from lib.auto_label.query_engine_config import get_kb_dir
		kb_directory = get_kb_dir(config)
		rule_file = os.path.join(kb_directory, use_case, rules_file)
	else:
		rule_file = get_rules_file(config, use_case)
		rules_file = os.path.basename(rule_file)  # Extract filename for metadata
	
	if not os.path.exists(rule_file):
		raise FileNotFoundError(f"Rule file not found: {rule_file}")
	
	# Load CSV - create with headers from config if doesn't exist
	if not os.path.exists(csv_path):
		if not config or 'dataset' not in config or 'columns' not in config['dataset']:
			raise ValueError(f"Config file must contain dataset.columns to create CSV for use case: {use_case}")
		
		import csv
		with open(csv_path, 'w', newline='', encoding='utf-8') as f:
			writer = csv.writer(f)
			headers = get_csv_headers(config)
			writer.writerow(headers)
	
	df = pd.read_csv(csv_path)
	
	# Initialize Prolog and load ALL rules (including helper predicates for chaining)
	prolog = Prolog()
	prolog.consult(rule_file)
	
	# Extract label predicates and all rules
	# label_predicates: only predicates that output labels (for querying)
	# all_rules: all rules loaded into Prolog (enables chain rule inference)
	label_predicates, all_rules = extract_predicates_from_rules(rule_file)
	
	print(f"\nChain rule support enabled: Prolog will follow helper predicates automatically")
	predicates = label_predicates
	
	# Build column mapping from config
	column_mapping, prolog_var_names = build_column_mapping(config)
	
	# Label each row
	labels = []
	for idx, row in df.iterrows():
		label = label_single_row(prolog, row, idx, predicates, column_mapping, prolog_var_names, multi_label)
		labels.append(label)
	
	# Add labels and rules file metadata to dataframe
	df[label_column] = labels
	df['rules_file'] = rules_file  # Add column showing which rules file was used
	
	# Use output path from config if available, otherwise append _labeled
	from lib.auto_label.query_engine_config import get_output_csv_path
	if config:
		output_path = get_output_csv_path(config)
	else:
		output_path = csv_path.replace('.csv', '_labeled.csv')
	
	df.to_csv(output_path, index=False)
	print(f"Labeled {len(df)} rows. Results saved to {output_path}")
	
	return df


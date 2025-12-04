import os
import json
from datetime import datetime

def load_config(use_case, kb_dir="KB"):
	"""
	Load configuration file for the use case.
	
	Args:
		use_case (str): The use case name (e.g., 'PM_Temperature', 'useCase2')
		kb_dir (str): Directory where knowledge base files are stored
		
	Returns:
		dict: Configuration dictionary or None if not found
	"""
	config_file = os.path.join(kb_dir, use_case, "config.json")
	if os.path.exists(config_file):
		with open(config_file, 'r', encoding='utf-8') as f:
			return json.load(f)
	return None

def get_kb_dir(config, default="KB"):
	"""
	Get knowledge base directory from config.
	
	Args:
		config (dict): Configuration dictionary
		default (str): Default KB directory
		
	Returns:
		str: KB directory path
	"""
	if config and 'paths' in config:
		return config['paths'].get('kb_dir', default)
	return default

def get_data_dir(config, default="data"):
	"""
	Get data directory from config.
	
	Args:
		config (dict): Configuration dictionary
		default (str): Default data directory
		
	Returns:
		str: Data directory path
	"""
	if config and 'paths' in config:
		return config['paths'].get('data_dir', default)
	return default

def get_rules_file(config, use_case, default="generated_rules.pl"):
	"""
	Get rules file path from config.
	
	Args:
		config (dict): Configuration dictionary
		use_case (str): Use case name
		default (str): Default rules filename
		
	Returns:
		str: Full path to rules file
	"""
	kb_dir = get_kb_dir(config)
	filename = default
	if config and 'paths' in config:
		filename = config['paths'].get('rules_file', default)
	return os.path.join(kb_dir, use_case, filename)

def get_source_csv_path(config, default="data.csv"):
	"""
	Get source CSV file path from config.
	
	Args:
		config (dict): Configuration dictionary
		default (str): Default CSV filename
		
	Returns:
		str: Full path to source CSV file
	"""
	data_dir = get_data_dir(config)
	filename = default
	if config and 'paths' in config:
		filename = config['paths'].get('source_csv', default)
	return os.path.join(data_dir, filename)

def get_output_csv_path(config, default_pattern="labeled_{date}.csv"):
	"""
	Get output CSV file path from config with date substitution.
	
	Args:
		config (dict): Configuration dictionary
		default_pattern (str): Default output filename pattern
		
	Returns:
		str: Full path to output CSV file with today's date
	"""
	data_dir = get_data_dir(config)
	pattern = default_pattern
	if config and 'paths' in config:
		pattern = config['paths'].get('output_csv_pattern', default_pattern)
	
	# Substitute {date} with today's date and {datetime} with full datetime
	today_str = datetime.today().strftime('%Y%m%d')
	datetime_str = datetime.today().strftime('%Y%m%d_%H%M%S')
	filename = pattern.format(date=today_str, datetime=datetime_str)
	return os.path.join(data_dir, filename)

def build_column_mapping(config):
	"""
	Build column mapping from config.
	
	Args:
		config (dict): Configuration dictionary
		
	Returns:
		tuple: (column_mapping dict, prolog_var_names list)
			- column_mapping: {prolog_name: csv_column}
			- prolog_var_names: list of Prolog variable names
	"""
	column_mapping = {}
	prolog_var_names = []
	if config and 'prolog_variables' in config:
		for var in config['prolog_variables']:
			column_mapping[var['prolog_name']] = var['csv_column']
			prolog_var_names.append(var['prolog_name'])
	return column_mapping, prolog_var_names

def build_variable_descriptions(config):
	"""
	Build variable descriptions from config for prompt generation.
	
	Args:
		config (dict): Configuration dictionary
		
	Returns:
		str: Formatted variable descriptions
	"""
	var_descriptions = ""
	if config and 'dataset' in config and 'columns' in config['dataset']:
		var_descriptions = "\n\\Information:\n"
		for col in config['dataset']['columns']:
			if col['type'] in ['numeric', 'categorical']:
				desc = col.get('description', col['name'])
				var_descriptions += f"- {col['prolog_name']}: {desc} (จากคอลัมน์ '{col['name']}')\n"
	return var_descriptions

def get_prompt_template(config):
	"""
	Get prompt template from config or return default.
	
	Args:
		config (dict): Configuration dictionary
		
	Returns:
		str: Prompt template with placeholders {var_descriptions} and {user_input}
	"""
	if config and 'prompt_template' in config:
		return config['prompt_template']
	
	# Default template
	return """Translate natural language to First Order Logic Prolog (output only code, 1 rule per line, no markdown or explanation)

Important Prolog rules:
- Use format: predicate_name(Variable, 'label') :- condition.
- For labeling rules, the label must be the second argument with single quotes
- Use lowercase for predicates and Variables must start with uppercase
- Use correct Prolog operators: =< (less than or equal), >= (greater than or equal), > (greater than), < (less than)
{var_descriptions}
Example format:
label_air_pollution(PM2_5, 'low pollution') :- PM2_5 =< 15.
label_air_pollution(PM2_5, 'moderate pollution') :- PM2_5 > 15, PM2_5 =< 35.
label_air_pollution(PM2_5, 'high pollution') :- PM2_5 > 35.

User command: {user_input}"""

def get_label_column(config, default='auto_label'):
	"""
	Get label column name from config.
	
	Args:
		config (dict): Configuration dictionary
		default (str): Default label column name
		
	Returns:
		str: Label column name
	"""
	if config and 'labeling' in config:
		return config['labeling'].get('label_column', default)
	return default

def get_multi_label_mode(config, default=False):
	"""
	Get multi-label mode setting from config.
	
	Args:
		config (dict): Configuration dictionary
		default (bool): Default multi-label mode
		
	Returns:
		bool: True if multi-label mode is enabled
	"""
	if config and 'labeling' in config:
		return config['labeling'].get('multi_label', default)
	return default

def get_csv_headers(config, default_headers=None):
	"""
	Get CSV headers from config dataset columns.
	
	Args:
		config (dict): Configuration dictionary
		default_headers (list): Default headers if config not available
		
	Returns:
		list: List of column names
	"""
	if config and 'dataset' in config and 'columns' in config['dataset']:
		return [col['name'] for col in config['dataset']['columns']]
	return default_headers

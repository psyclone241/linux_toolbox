# Helper script for setting up your apps local instance
# Contributors:
# Roy Keyes <keyes@ufl.edu>

help:
	@echo "Available tasks :"
	@echo "\tconfig - Make a copy of the config file"
	@echo "\tsetup - Run the virtualenv setup"
	@echo "\twatch - Run the watch task"
	@echo "\twatchquiet - Run the watch task in quiet mode"

config:
	cp config.example.ini config.ini
	open config.ini

setup:
	virtualenv venv
	venv/bin/pip install -r requirements.txt

watch:
	@python processwatch.py

watchquiet:
	@python processwatch.py -q

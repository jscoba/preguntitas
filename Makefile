test: test-server
	@echo "Testing done"

test-server:
	@cd quiz_server && python manage.py test

installdeps: install-deps-server
	@echo "Dependencies installed"

install-deps-server: 
	pip install -r quiz_server/requirements.txt

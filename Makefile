LOCAL_USERNAME := $(shell whoami)
REVISION := $(shell git log -n 1 --pretty=format:"%H")
HOSTNAME := 'greentogo'

.PHONY: deploy-staging deploy-production requirements server update_requirements

server: requirements
	tmux new-session './greentogo/manage.py runserver_plus' \; split-window -h 'ngrok http -subdomain=$(HOSTNAME) 8000'

requirements: requirements.txt dev-requirements.txt bower.json
	pip-sync requirements.txt dev-requirements.txt
	bower install

requirements.txt: requirements.in
	pip-compile requirements.in

dev-requirements.txt: dev-requirements.in
	pip-compile dev-requirements.in

update_requirements:
	pip-compile --upgrade requirements.in
	pip-compile --upgrade dev-requirements.in

deploy-staging:
	ansible-playbook -i deployment/environments/staging/hosts --vault-password-file=.password  deployment/playbook.yml
	curl https://api.rollbar.com/api/1/deploy/ \
		-F access_token=$(ROLLBAR_KEY) \
		-F environment=staging \
		-F revision=$(REVISION) \
		-F local_username=$(LOCAL_USERNAME)

deploy-production:
	ansible-playbook -i deployment/environments/production/hosts --vault-password-file=.password  deployment/playbook.yml
	curl https://api.rollbar.com/api/1/deploy/ \
		-F access_token=$(ROLLBAR_KEY) \
		-F environment=production \
		-F revision=$(REVISION) \
		-F local_username=$(LOCAL_USERNAME)

greentogo/greentogo/.env:
	cp greentogo/greentogo/.env.sample greentogo/greentogo/.env
	@echo
	@echo "You will need to add database and API information to"
	@echo "the greentogo/greentogo/.env file. See README.md for"
	@echo "more information."
	@echo

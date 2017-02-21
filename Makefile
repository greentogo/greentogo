ENVIRONMENT := production
LOCAL_USERNAME := $(shell whoami)
REVISION := $(shell git log -n 1 --pretty=format:"%H")

.PHONY: deploy requirements server

server: requirements
	tmux new-session './greentogo/manage.py runserver_plus' \; split-window -h 'ngrok http -subdomain=greentogo 8000'

requirements: requirements.txt bower.json
	pip-sync requirements.txt
	bower install

requirements.txt: requirements.in
	pip-compile requirements.in

deploy:
	ansible-playbook -i deployment/hosts  --vault-password-file=.password  deployment/playbook.yml
	curl https://api.rollbar.com/api/1/deploy/ \
		-F access_token=$(ROLLBAR_KEY) \
		-F environment=$(ENVIRONMENT) \
		-F revision=$(REVISION) \
		-F local_username=$(LOCAL_USERNAME)

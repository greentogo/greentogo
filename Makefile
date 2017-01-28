ENVIRONMENT := production
LOCAL_USERNAME := $(shell whoami)
REVISION := $(shell git log -n 1 --pretty=format:"%H")

.PHONY: deploy prod deps

requirements.txt: requirements.in
	pip-compile requirements.in

deps: requirements.txt
	pip-sync requirements.txt

deploy:
	ansible-playbook -i deployment/hosts  --vault-password-file=.password  deployment/playbook.yml
	curl https://api.rollbar.com/api/1/deploy/ \
		-F access_token=$(ROLLBAR_KEY) \
		-F environment=$(ENVIRONMENT) \
		-F revision=$(REVISION) \
		-F local_username=$(LOCAL_USERNAME)

prod:
	bower install
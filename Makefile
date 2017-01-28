.PHONY: deploy prod deps

requirements.txt: requirements.in
	pip-compile requirements.in

deps: requirements.txt
	pip-sync requirements.txt

deploy:
	ansible-playbook -i deployment/hosts  --vault-password-file=.password  deployment/playbook.yml

prod:
	bower install
.PHONY: deploy prod

deploy:
	ansible-playbook -i deployment/hosts  --vault-password-file=.password  deployment/playbook.yml

prod:
	bower install
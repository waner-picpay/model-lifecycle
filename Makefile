renew_token:				## Authenticate to Google account and fill in environment variables.
	## PROFILE=<your_profile>, default profile is sts
	aws-google-auth -p $(or $(PROFILE),sts) && python3 renew_token.py $(or $(PROFILE),sts)
build_up: 
	docker-compose up --build --force-recreate
down:
	docker-compose down
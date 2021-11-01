makemigrations:
	docker-compose exec backend python manage.py makemigrations $(c)

migrate:
	docker-compose exec backend python manage.py migrate $(c)

shell:
	docker-compose exec backend python manage.py shell $(c)

build:
	docker-compose -f docker-compose.yml build $(c)

up:
	docker-compose -f docker-compose.yml up -d $(c)

start:
	docker-compose -f docker-compose.yml start $(c)

down:
	docker-compose -f docker-compose.yml down $(c)

destroy:
	docker-compose -f docker-compose.yml down -v $(c)

stop:
	docker-compose -f docker-compose.yml stop $(c)

restart:
	docker-compose -f docker-compose.yml stop $(c)
	docker-compose -f docker-compose.yml up -d $(c)

logs:
	docker-compose -f docker-compose.yml logs --tail=100 -f $(c)

logs-backend:
	docker-compose -f docker-compose.yml logs --tail=100 -f backend

ps:
	docker-compose -f docker-compose.yml ps

login-db:
	docker-compose -f docker-compose.yml exec db /bin/bash

login-backend:
	docker-compose -f docker-compose.yml exec backend /bin/bash

db-shell:
	docker-compose -f docker-compose.yml exec db psql -Upostgres
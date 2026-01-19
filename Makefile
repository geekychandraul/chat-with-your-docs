web-service := backend_test_rag

config_file:= src/config/serverlocal.cfg
temp_file := src/config/temp_config.mk

# Process the config file, removing headers and quotes
ifneq ("$(wildcard $(config_file))","")
    # Create a temporary file with processed variables
    $(shell grep -v '^\[' $(config_file) | sed 's/"//g' > $(temp_file))
    include $(temp_file)
endif


db-service := $(POSTGRES_SERVER)
db-schema := $(POSTGRES_DB_SCHEMA)
db := $(POSTGRES_DB)
db-user := $(POSTGRES_USER)

init:
	make run_server && \
	sleep 3 && \
	make db_migrate
# 	make create_schema && \

run_server:
	@docker compose up -d backend db gradio


up:
	@docker compose up

build:
	@docker compose build

down:
	@docker compose down

test:
	@docker exec -it $(web-service) sh -c "coverage run --source app -m pytest $(path) -v -s && coverage report -m"


create_schema:
	@docker exec -it $(db-service) sh -c 'psql -U $(db-user) -d $(db) -c "CREATE SCHEMA IF NOT EXISTS $(db-schema)"'

create_migration:
	@docker exec -it $(web-service) sh -c 'alembic revision --autogenerate -m "$(m)"'

db_migrate:
	@docker exec -it $(web-service) sh -c 'alembic upgrade head'


db_revision:
	@docker exec -it $(web-service) sh -c "alembic revision --autogenerate -m '$(message)'"

db_upgrade:
	@docker exec -it $(web-service) sh -c "alembic upgrade head"

db_downgrade:
	@docker exec -it $(web-service) sh -c "alembic downgrade -1"

create_api_doc:
	@docker exec -it $(web-service) sh -c "python extract-openapi.py app.app_definition:app"

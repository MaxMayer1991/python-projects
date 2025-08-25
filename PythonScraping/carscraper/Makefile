.PHONY: up up-dev down logs

up:
	docker-compose up -d

up-dev:
	SPIDER_TIME=8:00 DUMP_TIME=20:00 docker-compose up -docker

down:
	docker-compose down

logs:
	docker-compose logs -f scrapy_app

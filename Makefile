install:
		poetry install
project:
		poetry run project
build:
		poetry build
publish:
		poetry publish --dry-run
package-install:
	@echo "Удаляем старые версии пакета..."
	python3 -m pip uninstall project-2-egorov-m25-555 -y || true
	@echo "Очищаем папку dist..."
	rm -rf dist/*
	@echo "Собираем пакет..."
	poetry build
	@echo "Устанавливаем пакет..."
	python3 -m pip install dist/*.whl
lint:
		poetry run ruff check .

.PHONY: ayuda instalar pruebas nodo topologia limpiar

ayuda:
	@echo "make instalar          crea el entorno virtual e instala dependencias"
	@echo "make pruebas           corre las pruebas unitarias"
	@echo "make nodo ID=A         levanta un solo nodo"
	@echo "make topologia         levanta los nueve nodos en local"
	@echo "make limpiar           borra artefactos de ejecucion"

instalar:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	@echo "listo: activa el entorno con 'source .venv/bin/activate'"

pruebas:
	python3 -m pytest -q

nodo:
	@test -n "$(ID)" || (echo "uso: make nodo ID=A" && exit 1)
	python3 nodo.py --id $(ID)

topologia:
	bash scripts/levantar_topologia.sh

limpiar:
	rm -rf estado bitacoras .pytest_cache
	rm -f *_tabla_enrutamiento.csv
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

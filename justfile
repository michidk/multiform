run:
    python3 start.py --verbosity trace transpile --architecture example/architecture.yaml --templates example/templates --report

plot:
    python3 start.py --verbosity trace plot --architecture example/architecture.yaml --out out/graph.dot
    dot -Tjpg out/graph.dot -o out/graph.jpg

validate:
    cd ./out/aws && terraform validate
    cd ./out/gcp && terraform validate

clean:
    rm -rf out/

sort:
    isort ./src

fmt:
    black ./src

lint:
    pylint ./src

install-dev:
    pip install pylint black isort

install:
    pip install -e .

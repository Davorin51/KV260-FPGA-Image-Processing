CXX ?= g++
PYTHON ?= python
CXXFLAGS ?= -std=c++14 -O2 -Wall -Wextra -Wpedantic -Wconversion -Werror
HEADERS = hls/include/grayscale_core.hpp host/cpp/memory_transport.hpp

.PHONY: all cpp-test test lint demo sanitize hls-csim
all: build/grayscale_cpu build/test_grayscale

build:
	mkdir -p build

build/grayscale_cpu: host/cpp/grayscale_cpu.cpp $(HEADERS) | build
	$(CXX) $(CXXFLAGS) $< -o $@

build/test_grayscale: tests/test_grayscale.cpp $(HEADERS) | build
	$(CXX) $(CXXFLAGS) $< -o $@

cpp-test: build/test_grayscale
	./build/test_grayscale

test: all cpp-test
	$(PYTHON) -m pytest --cov=kv260_image --cov-fail-under=85

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

sanitize: | build
	$(CXX) -std=c++14 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer tests/test_grayscale.cpp -o build/test_grayscale_sanitize
	./build/test_grayscale_sanitize

hls-csim:
	$(PYTHON) scripts/run_hls.py --stage csim

demo: build/grayscale_cpu
	$(PYTHON) -m kv260_image demo --cpp build/grayscale_cpu --output build/demo

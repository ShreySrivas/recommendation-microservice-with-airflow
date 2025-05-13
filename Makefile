# Makefile in recsys/

.PHONY: build-images

# Builds both the stream and trainer Docker images
build-images:
	docker build -t recsys_stream:latest ./stream
	docker build -t recsys_trainer:latest ./training

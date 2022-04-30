docker build -t tldrd0117/fin-crawling-server .
docker push tldrd0117/fin-crawling-server


#multi platform build
docker buildx build --platform linux/amd64,linux/arm64 . -t tldrd0117/fin-crawling-server   
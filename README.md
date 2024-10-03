# Knowledge Graph Demo

## Running Neo4j on docker

```
cp .env.example .env
docker-compose up neo4j
```

open http://localhost:7474


### Dumping your neo4j DB
```
docker-compose stop neo4j
docker-compose run neo4j neo4j-admin database dump neo4j
```

## Importing a Dump File
```
docker-compose run neo4j neo4j-admin database load --from-path=/data/dumps/ --overwrite-destination=true neo4j
```
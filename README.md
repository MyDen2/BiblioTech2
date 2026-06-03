# BiblioTech2

## Lancer Docker
docker compose up -d

## Créer les buckets Minio 

python -m src.init.init_minio

## Charger les fichiers dans MinIO

python -m src.etl.loaders.load_books
python -m src.etl.loaders.load_ratings

## Faire les transformations

python -m src.etl.transformers.clean_books
python -m src.etl.transformers.clean_ratings
python -m src.etl.transformers.build_ratings_joinable

## Faire les Gold

python -m src.etl.transformers.build_book_popularity
python -m src.etl.transformers.build_user_profiles

## Charger PostgreSQL

python -m src.database.load_books_to_postgres

## Sélection des livres à enrichir (pour IA)

python -m src.etl.transformers.select_books_to_enrich

==> Création de gold/books_to_enrich.parquet contenant  les 5000 livres les plus pertinents.


## Enrichissement 

python -m src.enrichment.enrich_books_metadata

## Ordre complet :

python -m src.init.init_minio
python -m src.etl.loaders.load_books
python -m src.etl.loaders.load_ratings
python -m src.etl.transformers.clean_books
python -m src.etl.transformers.clean_ratings
python -m src.etl.transformers.build_ratings_joinable
python -m src.etl.transformers.build_book_popularity
python -m src.etl.transformers.build_user_profiles
python -m src.database.load_books_to_postgres
python -m src.etl.transformers.select_books_to_enrich
python -m src.enrichment.enrich_books_metadata
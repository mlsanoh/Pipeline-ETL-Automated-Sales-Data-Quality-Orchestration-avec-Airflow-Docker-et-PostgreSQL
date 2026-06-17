FROM quay.io/astronomer/astro-runtime:11.3.0

USER root

# Dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
RUN pip install loguru

USER airflow
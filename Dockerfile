# Use Python 3.8 because LexNLP 2.3.0 requires it
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Download NLTK data
RUN python -m nltk.downloader punkt averaged_perceptron_tagger maxent_ne_chunker words

# Download spaCy English model
RUN python -m spacy download en_core_web_sm

# Copy app code
COPY . .

# Copy and prepare startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Run the app
CMD ["/start.sh"]

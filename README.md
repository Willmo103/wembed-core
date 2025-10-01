# wembed_core
The core library for 'Wembed'

## Overview
`wembed_core` is a python library that provides essential functionalities for the 'Wembed' project.
It will include all database models, utility functions, and core logic required for the application to function.

## Features
- Code Modeling and representation ins various ways:
  - Dependency Graphs
  - Sparce Vector representations
  - Abstract Syntax Trees (AST)
  - line embeddings
  - Git repository metadata
  - Host File system metadata
  - Tree Views

- Advanced Filesystem Scanning and Monitoring:
  - Recursive directory scanning
  - File type detection and classification
  - Change detection and versioning
  - Configurable scanning parameters
  - FileType dependant formatting and parsing
  - FileType dependant embedding strategies

- Webscraping and Data Extraction:
  - Automated web ingestion and parsing
  - Support for various data formats (HTML, JSON, XML, etc.)
  - Content Transformation and normalization via Docling
  - Metadata extraction and enrichment

- Vector Store Integration:
  - Support for Qdrant and local database vector stores
  - Efficient storage and retrieval of high-dimensional vectors
  - Similarity search and nearest neighbor queries and background indexing
  - Background data annotation and enrichment processors

- Embedding Generation:
  - Entirely localized embedding generation using open-source models
  - Support for various embedding models and configurations
  - Batch processing and parallelization for large datasets
  - Customizable embedding strategies based on file types and content

and more...
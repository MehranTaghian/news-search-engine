# Persian News Search Engine
A search engine for crawling news from the web, storing in a structured way, and querying through the stored
documents for finding the most relevant results using Machine Learning and Information Retrieval techniques.

## Instructions to run the search engine
Before running the server, you need to install the required packages. To do that, create a virtual 
environment and run 
```
$ pip install -r requirements.txt
```
The version of python used is `3.8.10`. Before running the search engine for the first time, issue
the following command:
```
$ python manage.py migrate
```
For running the search engine, use the following command:
```
$ python manage.py runserver
```

## Details of Implementation
This search engine is designed to retrieve the most relevant documents given a query by the user. The 
steps of implementation are comprised of 1) indexing and storing documents, 2) querying through documents.

### Indexing 
When a document is received, first some preprocessing steps including *Normalization*, *Tokenization*,
*Stemming*, and Removing stop words is done. Then the document is stored as a vector. For vectorizing, 
we need to accept a weighting scheme for weighting words within a document. For this purpose, 
[TF-IDF](https://en.wikipedia.org/wiki/Tf%E2%80%93idf) method is used. 

### Querying
When a query is provided by the user, first the query is converted to a vector using the same process as used
for documents (TF-IDF). Then the similarity of the query to each document is calculated using the 
[Cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity). Then, *K* most similar documents to the query
are returned.

According to Wikipedia, we can have different combinations of weighting schemes for both query and documents. 
The weighting schemes we have implemented are as the following table:

![](./Images/tf-idf-weighting.png)

*Different weighting scheme for converting documents and queries to vectors*

In this table, $f_{t, d}$ is the number of repetitions of the word $t$ in document $d$, $f_{t, q}$ is the repetition of 
$t$ in query $q$, and $n_t$ is the number of documents containing word $t$.
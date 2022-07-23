# Persian News Search Engine
A search engine for crawling news from the web, storing in a structured way, and querying through the stored
documents for finding the most relevant results using Machine Learning and Information Retrieval techniques.

### Instructions to run the search engine
Before running the server, you need to install the required packages. To do that, create a virtual 
environment and run 
```
$ pip install -r requirements.txt
```
The version of python used is `3.8.10`. To run the search engine for the first time, issue
the following command:
```
$ python manage.py migrate
```
for later runs, use the following command
```
$ python manage.py runserver
```

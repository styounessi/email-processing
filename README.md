<h1 align="center">
Email Processing Pipeline
</h1>

An email processing pipeline that collects unread emails from a dedicated product feedback inbox, analyzes the content of the email for sentiment, and uploads the records to MongoDB.

![Flow](https://i.imgur.com/77Y1hnc.png)

## What's the idea? 
If a product or service has a dedicated inbox for customer/user feedback submissions via email, it would be nice to have all that data stored somewhere and pre-processed for sentiment.
The idea is to automate the process along these general steps:

1. Check an inbox (in this case Gmail) on a daily basis.
2. Pull new, unread emails and save the Sender, Subject line, Date/Time, and Body of the email to a parquet file. 
3. Perform [NLTK VADER](https://www.nltk.org/_modules/nltk/sentiment/vader.html) sentiment analysis on new files.
4. Insert fully processed records to [MongoDB](https://www.mongodb.com/docs/manual/core/databases-and-collections/).
5. Remove parquet files that are older than the retention period (default = 7 days).

⚠️ Keep in mind that this is a simple idea done purely for fun/interest, there are *many* things that would be done differently in real-world circumstances.

## Technologies/Services
### Apache Airflow
Airflow is open source and helps orchestrate workflows programmatically. Airflow can be as complex or simple as you like depending on one's needs but the general architecture revolves around:
- 🕑 Scheduler, which handles both triggering scheduled workflows, and submitting Tasks to the executor to run.
- 🧑‍🏭 Executor & Worker, which handles running tasks.
- 💻 Webserver, which presents a UI to inspect, trigger and debug the behaviour of DAGs (more on this below) and tasks.
- 💾 Metadata database, used by the different services above.

#### DAGs 
A DAG (Directed Acyclic Graph) is the core concept of Airflow, collecting Tasks together, organized with dependencies and relationships to say how they should run. DAGs are primarily written in Python but do nothing without tasks to run.

> The DAG itself doesn’t care about what is happening inside the tasks; it is merely concerned with how to execute them - the order to run them in, how many times to retry them, if they have timeouts, and so on.

This project uses the `BashOperator` to run the tasks in the DAGs by executing the `.py` files entirely rather than importing functions and using the `PythonOperator`

### Docker 🐋 & Docker Compose 🐙

#### Docker 🐋
> A Docker container is a lightweight and isolated executable unit that encapsulates an application and its dependencies, including libraries, binaries, and configuration files. This project uses Docker extensively to make the application portable and consistent. 

The `Dockerfile` included here merely extends the `apache/airflow` image to include the Python library dependencies needed for this project.

#### Docker Compose 🐙
> Docker Compose is a tool that was developed to help define and share multi-container applications. With Compose, we can create a YAML file to define the services and with a single command, can spin everything up or tear it all down.

The `docker-compose.yml` file included here defines the multi-container environment for running Airflow with PostgreSQL, Redis, and MongoDB included as supporting services. 

The Airflow services inherit configurations defined in `x-airflow-common` with extended configurations for each service as well.

`postgres-db-volume` and `mongodb-volume` are defined as volumes for data persistence since containers are inherently ephemeral so this ensures that data persists beyond any single container instance.

Everything is spun up together using `docker compose up`.

### MongoDB 🥬
> MongoDB is a popular open-source NoSQL database that uses a flexible document model, known as BSON, for data storage. It is designed for scalability, high performance, and ease of development, making it suitable for handling large amounts of unstructured or semi-structured data

It makes sense to use MongoDB for this project since the records are simple and have no relational complexities. They are inserted in the `productDB` under the `emails` collection. Collections do not enforce a schema, allowing for flexible and dynamic data structures.

![Mongo](https://i.imgur.com/ih2RDY7.gif)

### NLTK (Natural Language Toolkit) VADER (Valence Aware Dictionary and sEntiment Reasoner) 🌠
> NLTK VADER is a rule-based sentiment analysis tool specifically designed for analyzing sentiment in text. It is part of the NLTK library, a popular Python package for natural language processing.

The body of each email is analyzed by the `SentimentIntensityAnalyzer` and a new field called `sentiment` is added with the derived sentiment (via the compound score) of each email. 

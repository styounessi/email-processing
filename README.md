<h1 align="center">
Email Processing Pipeline 📧
</h1>

An email processing pipeline that collects unread emails from a dedicated product feedback inbox, analyzes the content of the emails for sentiment, and uploads the records to a MongoDB database.

![Flow](https://i.imgur.com/Om8rBWY.png)

## What's the idea? 🤔
The idea behind this project is to automate the process of collecting customer/user feedback submissions via email and storing the data for sentiment analysis. The pipeline follows these general steps:

1. Check the designated inbox (e.g., Gmail) on a daily basis.
2. Fetch new, unread emails and save the Sender, Subject Line, Date/Time, and Body of the email(s) to a parquet file. 
3. Perform sentiment analysis on the email content using [NLTK VADER](https://www.nltk.org/_modules/nltk/sentiment/vader.html).
4. Insert the fully processed records into a [MongoDB](https://www.mongodb.com/docs/manual/core/databases-and-collections/) database.
5. Remove parquet files that are older than the retention period. 

⚠️ Please note that this project is designed for fun/interest and **will not** reflect real-world implementation. Certain components like `triggerer`, `cli`, and `flower` have been intentionally omitted to prioritize lightweight development. These components are typically included in more comprehensive Airflow environments.

## Technologies/Services
### Apache Airflow ♻️
Apache Airflow is an open-source platform for programmatically orchestrating workflows. Airflow can be as complex or simple as you like and generally follows the following architecture:

- 🕑 Scheduler, which handles both triggering scheduled workflows, and submitting tasks to the executor to run.
- 👷‍♂️ Executor & Worker, which handles running tasks.
  - > Executors are the mechanism by which task instances get run. They have a common API and are “pluggable”, meaning you can swap executors based on your installation needs.
  - Read more about [Executors and Executor Types](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/executor/index.html).
- 💻 Webserver, which presents a UI to inspect, trigger and debug the behaviour of DAGs (more on this below) and tasks.
- 💾 Metadata database, used by the different services above.

#### DAGs 🔄
Directed Acyclic Graphs (DAGs) are the core concept of Airflow, representing workflows with tasks and dependencies. In this project, the tasks are executed using the `BashOperator` to run the `.py` files directly.

> The DAG itself doesn’t care about what is happening inside the tasks; it is merely concerned with how to execute them - the order to run them in, how many times to retry them, if they have timeouts, and so on.

Read more about [DAGs](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html) and [different types of Operators](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/operators.html). 

### Docker 🐋 & Docker Compose 🐙

#### Docker 🐋
> A Docker container is a lightweight and isolated executable unit that encapsulates an application and its dependencies, including libraries, binaries, and configuration files.

This project uses Docker to ensure portability and consistency. The included `Dockerfile` extends the `apache/airflow` base image with necessary core Python libraries.

> **Note**
> Please keep in mind that, despite the way the flow chart for this pipeline is depicted, <ins>each</ins> Airflow service is a separate Docker container. They are just grouped together visually because they are components of Airflow.

#### Docker Compose 🐙
> Docker Compose is a tool that was developed to help define and share multi-container applications. With Compose, we can create a YAML file to define the services and with a single command, can spin everything up or tear it all down.

The `docker-compose.yml` file included here defines the multi-container environment for running Airflow with PostgreSQL, Redis, and MongoDB included as supporting services. 

The Airflow services inherit configurations defined in `x-airflow-common`, while also having their own individual configurations specific to each service.

Volumes `postgres-db-volume` and `mongodb-volume` are defined as volumes to enable data persistence across containers. Since containers are inherently ephemeral, these volumes ensure that data persists beyond the lifespan of any individual container.

Everything is spun up together using `docker compose up` when ready. 

### NLTK (Natural Language Toolkit) VADER (Valence Aware Dictionary and sEntiment Reasoner) 🌠
> NLTK VADER is a rule-based sentiment analysis tool specifically designed for analyzing sentiment in text. It is part of the NLTK library, a popular Python package for natural language processing.

The content of each email is analyzed using the `SentimentIntensityAnalyzer` and the resulting sentiment is derived from its compound score. A new field called `sentiment` is then added to each email, recording the derived sentiment.

Once a file has been processed for sentiment, its contents are ready to be inserted into the `emails` collection.

### MongoDB 🥬
> MongoDB is a popular open-source NoSQL database that uses a flexible document model, known as BSON, for data storage. It is designed for scalability, high performance, and ease of development, making it suitable for handling large amounts of unstructured or semi-structured data.

It makes sense to use MongoDB for this project since the records are simple and have no relational complexities. They are inserted in the `productDB` under the `emails` collection. Collections do not enforce a schema, allowing for flexible and dynamic data structures.

![Mongo](https://i.imgur.com/ih2RDY7.gif)

Processed and stored records will look like this example once they are inserted into the collection:

```
    _id: ObjectId("64c31ba93851089f36d47d67"),
    from: 'Jane Smith <feedbackgiver123@proton.me>',
    subject: 'Terrible service - very unhappy',
    body: 'Your product and customer service is awful. I will never buy again!!!!',
    date: 'Wed, 14 Jun 2023 00:56:52 +0000',
    sentiment: 'Negative'
```
### Environment Variable File 🔑

This repository includes an `.env.example` file, which serves as a template for configuring environment variables related to Gmail and Airflow/Postgres. To use these variables, you'll need to rename this file to `.env` and enter values for the variables. The snippet below shows the complete structure of the file:

```env
# Incoming Mail (IMAP) server address for Gmail
GMAIL_IMAP_SERVER=

# Should contain the Gmail address used for reading and extracting inbox emails
GMAIL_ADDRESS=

# Please note that instead of a regular Gmail password, this variable should contain an "app code" instead
# An app code is a secure way to authenticate an application without revealing the actual Gmail password
# To create an app code, follow these steps:
# 1. Go to your Google Account settings (https://myaccount.google.com/security)
# 2. In the "Security" section, select "App passwords"
# 3. Generate a new app password for your application, and use that generated code here
GMAIL_PASSWORD=

# Represents the user ID (UID) that the Airflow application will use. It is typically used for setting permissions
# and access control
AIRFLOW_UID=

# Postgres service variables
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=

# Airflow web interface credentials
_AIRFLOW_WWW_USER_USERNAME=
_AIRFLOW_WWW_USER_PASSWORD=
```

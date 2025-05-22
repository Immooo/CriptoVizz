
<h1 align="center">Crypto-Viz</h1>

<p align="center">
  <a href="#dart-about">About</a> &#xa0; | &#xa0; 
  <a href="#sparkles-features">Features</a> &#xa0; | &#xa0;
  <a href="#rocket-technologies">Technologies</a> &#xa0; | &#xa0;
  <a href="#white_check_mark-requirements">Requirements</a> &#xa0; | &#xa0;
  <a href="#office-Architecture">Architecture</a> &#xa0; | &#xa0;
  <a href="#checkered_flag-starting">Starting</a> &#xa0; | &#xa0;
  <a href="#family-Team">Team</a> &#xa0; | &#xa0;
  <a href="#memo-license">License</a> &#xa0; | &#xa0;
</p>

<br>

## :dart: About ##

Scraping cryptocurrency news feed and continuously process the collected data. Provide analytics dynamically with the appropriate graphs.


Volumes from Docker are push for saving all datas (Ex : Grafana) [DON'T DO THAT IN NORMAL CASE]

## :sparkles: Features ##

:heavy_check_mark: continuously collect data from a cryptocurrency news feed ;\
:heavy_check_mark: Store the data in a queue in order to be able to multiply the input sources ;\
:heavy_check_mark: continuously process the collected data and provide analytics ;\
:heavy_check_mark: Automatically clear data in order to lighten the database over time;\
:heavy_check_mark: A queue consumption in order to be able to choose the frequency of updating the database;\
:heavy_check_mark: dynamically visualize the provided analytics with the appropriate graphs ;\


## :rocket: Technologies ##

The following tools were used in this project:

- [Python](https://www.python.org/downloads/release/python-3110/)
- [Docker](https://www.docker.com/)
- [Git](https://git-scm.com)
- [Mysql](https://www.mysql.com/)
- [RabbitMQ](https://www.rabbitmq.com/)
- [Grafana](https://grafana.com/)

<h3>Libraries : </h3>

- **beautifulsoup4**: A Python library for pulling data out of HTML and XML files. It provides easy ways to navigate, search, and modify the parse tree.

- **python-dotenv**: A Python library that helps manage environment variables in a project by loading variables from a .env file into the environment.

- **mysql-connector-python**: A MySQL connector library for Python, enabling communication between Python applications and MySQL databases.

- **requests**: A popular Python library for making HTTP requests. It simplifies the process of sending HTTP requests and handling the response.

- **datetime**: A built-in Python module for working with dates and times. It provides classes for representing dates, times, and intervals.

- **lxml**: A Python library for processing XML and HTML. It is a high-performance library, making it suitable for parsing large documents.

- **timedelta**: While not a standalone library, it's part of the Python standard library within the datetime module. It represents the duration between two dates or times.

- **pika**: A Python library for interacting with RabbitMQ, allowing for the creation, consumption, and management of messages in a RabbitMQ queue.

## :white_check_mark: Requirements ##

Before starting :checkered_flag:, you need to have [Git](https://git-scm.com), [Docker](https://www.docker.com/) and [Python](https://www.python.org/downloads/release/python-3110/) installed.

## :office: Architecture ##

The **architecture** working. As you may see, we scrape data in Python from the **Crypto** site every minute. Then the data is sent to a **RabbitMQ** queue in order to store it and allow multiple sites to be scraped. Another Python script (**Consumer**), consumes the **RabbitMQ** queue and saves it to the **database**. From this moment on, the data is saved. In order to lighten the **database**, every hour a Python script filters data more than 1 day old and clears half of them. **Grafana** directly queries the **database** and fills in the graphs we made.  

![architecture.png](docs%2Farchitecture.png)  


<h3>Seeder : </h3>
To simplify use, during the first launch so as not to have an empty database, we have a Seeder, which adds 50,000 rows to the database. This way it is possible to get an overview of the usefulness of the graphs.


<h3>Database : </h3>

The selected data are the most **suitable** for a simple reading of developments.  
![database.png](docs%2Fdatabase.png)


<h3>Process GitFlow : </h3>  

We use **Gitflow** for the aspect that is a branching model for **Git** that helps manage and organize the development process. It defines **specific branches** for features, releases, and hotfixes, facilitating collaboration and version control in **software development**.


<h3>Graphs : </h3>
- Candle Graph  


## :checkered_flag: Starting ##

```bash
# Clone this project
$ git clone https://github.com/EpitechMscProPromo2024/T-DAT-901-LYO_11

# Access
$ cd T-DAT-901-LYO_11


# Launch Docker and command line : 
$ docker compose up

#When process is done, you'll be able to access to the Grafana.

```


## :family: Team ##

**<h3>Scraping Module:</h3>**

- Develop a Python script to scrape data from the cryptocurrency news feed.
- Integrate BeautifulSoup for parsing HTML and XML data.
- Implement continuous data collection at regular intervals.
  
**<h3>Queue System:</h3>**

- Set up RabbitMQ as the message queue system.
- Create a Python script to store scraped data in the RabbitMQ queue.
- Implement a queue consumption mechanism to choose the frequency of updating the database.

**<h3>Data Processing and Analytics:</h3>**

- Develop a Python script (Consumer) to consume data from the RabbitMQ queue.
- Process the collected data and provide analytics dynamically.
- Utilize appropriate libraries such as MySQL Connector Python for database interaction.

**<h3>Database Management:</h3>**

- Set up MySQL as the database for storing processed data.
- Implement a mechanism to automatically clear old data from the database to lighten it over time.
- Consider using datetime and timedelta for managing time-related operations.

**<h3>Visualization Module:</h3>**

- Set up Grafana for dynamically visualizing analytics.
- Create graphs, such as candle graphs, to represent the processed data.
- Ensure Grafana can directly query the database for real-time updates.

**<h3>Dockerization:</h3>**

- Dockerize the entire project for easy deployment and scalability.
- Provide clear instructions in the README for launching the project using Docker Compose.

**<h3>GitFlow and Version Control:</h3>**

- Implement GitFlow for managing branches (features, releases, and hotfixes) to facilitate collaboration.
- Follow the defined GitFlow process during development.

**<h3>Seeder:</h3>**

- Develop a Seeder script to add initial data to the database during the first launch.
- Consider adding options for configuring the amount of seed data.

**<h3>Documentation:</h3>**

- Ensure that the README contains clear and concise instructions for setting up and running the project.
- Provide information on the project's architecture, technologies used, and any additional setup requirements.

## :memo: License ##

This project is under license from MIT. For more details, see the [LICENSE](https://github.com/TaviotBaptiste/Crypto-Viz/blob/main/LICENSE) file.


Made with :heart: by <a href="https://github.com/ArthurDufay" target="_blank">Arthur DUFAY</a> <a href="https://github.com/mamanin" target="_blank">Max MANIN</a> <a href="https://github.com/jojoricard" target="_blank">Joris RICARD</a>, <a href="https://github.com/ltournayre" target="_blank">LTournayre</a>, <a href="https://github.com/TaviotBaptiste" target="_blank">TaviotBaptiste</a>,

&#xa0;

<a href="#top">Back to top</a>

# Writing Subqueries with SQLAlchemy ORM

 Dealing directly with databases from applications can be challenging at times, that is why you need tools that act as an interface between the data layer and the core application. And the two most common tools available are SQL and ORM.
 In this article, you learn how to use SQLAlchemy ORM to interact with your database

 ## WHY ORM
 Rather than using SQL to interact with the database, ORM provides a method of interacting with a database using an object-oriented language
 and offers a layer of abstraction,
 - it improves your productivity as a developer, you don't have to remember the query differences between MySQL, PostgreSQL, SQLite, and others as it handles the low-level database interaction.
 -  Access to use your model classes and gives you an additional benefit that there is no possibility of a SQL injection.
 - Saves you the stress of writing a lot of code when mapping your raw SQL queries as data dictionaries, ORM  saves you from this

 There are advantages SQL offer over ORM in some critical performance situation such as seeing what exactly what is happening in the underlying database, making troubleshooting complex problems easier than when using ORM.
 Weigh up the advantages and disadvantages of both tools and make your choice.

 ### ORM in Action
 I will use the MYSQL database for this tutorial and will populate it using the following example data available on MySQL [docs](https://dev.mysql.com/doc/index-other.html)
```text
The Sakila sample database is made available by MySQL and is licensed via the New BSD license. Sakila contains data for a fictitious movie rental company and includes tables such as store, inventory, film, customer, and payment. 
```
#### Setting up mysql on  mac 
*Note: You can check up tutorials online on how to set up MYSQL for your operating system( Windows or Linux)*
```shell
brew install mysql
mysql_secure_installation
brew services start mysql
mysql -u root -p
```
### Load database after unzipping the Sakila zip folder available on MySQL [docs](https://dev.mysql.com/doc/index-other.html)
```shell
SOURCE /path_folder/Downloads/sakila-db/sakila-schema.sql;
SOURCE /path_folder/Downloads/sakila-db/sakila-data.sql;
USE sakila;
SHOW FULL TABLES;
```


Output:
```shell
mysql> SHOW FULL TABLES;
+----------------------------+------------+
| Tables_in_sakila           | Table_type |
+----------------------------+------------+
| actor                      | BASE TABLE |
| actor_info                 | VIEW       |
| address                    | BASE TABLE |
| category                   | BASE TABLE |
| city                       | BASE TABLE |
| country                    | BASE TABLE |
| customer                   | BASE TABLE |
| customer_list              | VIEW       |
| film                       | BASE TABLE |
| film_actor                 | BASE TABLE |
| film_category              | BASE TABLE |
| film_list                  | VIEW       |
| film_text                  | BASE TABLE |
| inventory                  | BASE TABLE |
| language                   | BASE TABLE |
| nicer_but_slower_film_list | VIEW       |
| payment                    | BASE TABLE |
| rental                     | BASE TABLE |
| sales_by_film_category     | VIEW       |
| sales_by_store             | VIEW       |
| staff                      | BASE TABLE |
| staff_list                 | VIEW       |
| store                      | BASE TABLE |
+----------------------------+------------+
```

### Creata a new user and grant access 

```shell
#create a new user and password, copy all this at once
CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';
GRANT ALL ON *.* TO 'username'@'localhost';
FLUSH PRIVILEGES;
```

### Set Up your Flask Application


- Clone this github repo 
- Create a virtual environment and install the extensions in requirements.txt file
- Update the env_sample with the following environment variables and your database credentials and run the following on your terminal 
```shell
$ export FLASK_ENV=development
$ export FLASK_APP=main.py
$ export SECRET_KEY="your secret key"
$ export DEV_DATABASE_URL="mysql+mysqldb://DB_USERNAME:DB_PASSWORD@127.0.0.1/DATABASE_NAME"
```
### Create the Migration Repository
Run the following command on your terminal
```shell
 $ flask db init 
 $ flask db migrate 
 $ flask db stamp head 

```
*OUTPUT* :
```shell
(env) $ flask db init                                                                          
  Creating directory /Users/apple/Desktop/Everyday_learning/complex_sql_queries/migrations ...  done
  Creating directory /Users/apple/Desktop/Everyday_learning/complex_sql_queries/migrations/versions ...  done
  Generating /Users/apple/Desktop/Everyday_learning/complex_sql_queries/migrations/script.py.mako ...  done
  Generating /Users/apple/Desktop/Everyday_learning/complex_sql_queries/migrations/env.py ...  done
  Generating /Users/apple/Desktop/Everyday_learning/complex_sql_queries/migrations/README ...  done
  Generating /Users/apple/Desktop/Everyday_learning/complex_sql_queries/migrations/alembic.ini ...  done
  Please edit configuration/connection/logging settings in '/Users/apple/Desktop/Everyday_learning/complex_sql_queries/migrations/alembic.ini' before proceeding.
(env)$ flask db migrate                                                                       
INFO  [alembic.runtime.migration] Context impl MySQLImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
/.../complex_sql_queries/migrations/env.py:85: SAWarning: Did not recognize type 'geometry' of column 'location'
  context.run_migrations()
INFO  [alembic.autogenerate.compare] Detected removed index 'idx_fk_film_id' on 'inventory'
INFO  [alembic.autogenerate.compare] Detected removed index 'idx_store_id_film_id' on 'inventory'
INFO  [alembic.autogenerate.compare] Detected removed table 'inventory'
INFO  [alembic.autogenerate.compare] Detected removed index 'idx_fk_country_id' on 'city'
INFO  [alembic.autogenerate.compare] Detected removed table 'city'
INFO  [alembic.autogenerate.compare] Detected removed index 'idx_fk_address_id' on 'store'
INFO  [alembic.autogenerate.compare] Detected removed index 'idx_unique_manager' on 'store'
INFO  [alembic.autogenerate.compare] Detected removed table 'store'
INFO  [alembic.autogenerate.compare] Detected removed index 'idx_title_description' on 'film_text'
......
  Generating /.../complex_sql_queries/migrations/versions/f6b945117232_.py ...  done

(env) $ flask db stamp head
INFO  [alembic.runtime.migration] Context impl MySQLImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running stamp_revision  -> f6b945117232
(env) oluchi@apples-Air-5 complex_sql_queries % 
```

### Auto-generate the models
```shell
sqlacodegen 'mysql://db_username:db_password@127.0.0.1/db_name' > app/models.py
```




### Write view functions
1. Generate a list of customer IDs along with the number of film rentals and the total payments
```sql
 SELECT c.first_name, c.last_name,
pymnt.num_rentals, pymnt.tot_payments
FROM customer c
INNER JOIN
(SELECT customer_id,
count(*) num_rentals, sum(amount) tot_payments
FROM payment
GROUP BY customer_id
) pymnt
ON c.customer_id = pymnt.customer_id;

```
2. Calculate the total revenues generated from PG-rated film rentals where the cast includes an actor whose last name starts with S. 
```sql
WITH actors_s AS
 (SELECT actor_id, first_name, last_name
 FROM actor
 WHERE last_name LIKE 'S%'
 ),
 actors_s_pg AS
 (SELECT s.actor_id, s.first_name, s.last_name,
 f.film_id, f.title
 FROM actors_s s
 INNER JOIN film_actor fa
 ON s.actor_id = fa.actor_id
 INNER JOIN film f
 ON f.film_id = fa.film_id
 WHERE f.rating = 'PG'
 ),
 actors_s_pg_revenue AS
 (SELECT spg.first_name, spg.last_name, p.amount
 FROM actors_s_pg spg
 INNER JOIN inventory i
 ON i.film_id = spg.film_id
 INNER JOIN rental r
 ON i.inventory_id = r.inventory_id
 INNER JOIN payment p
 ON r.rental_id = p.rental_id
 ) -- end of With clause
 SELECT spg_rev.first_name, spg_rev.last_name,
 sum(spg_rev.amount) tot_revenue
 FROM actors_s_pg_revenue spg_rev
 GROUP BY spg_rev.first_name, spg_rev.last_name
 ORDER BY 3 desc;

```
The following SQL Queries were gotten from the following book [Learning SQL by Alan Beaulieu] (https://www.amazon.com/Learning-SQL-Master-Fundamentals/dp/0596520832)



 ### Convert SQL queries to ORM Syntax
```python
@bp.route("/info", methods=("GET", "POST"))
def customer_IDs_with_filmRentals_and_totalPayments():

    stmt = (
        db.session.query(
            Payment.customer_id,
            db.func.count("*").label("num_rentals"),
            db.func.sum(Payment.amount).label("tot_payments"),
        )
        .group_by(Payment.customer_id)
        .subquery()
    )

    result = (
        db.session.query(
            Customer.first_name,
            Customer.last_name,
            stmt.c.num_rentals,
            stmt.c.tot_payments,
        )
        .join(stmt, Customer.customer_id == stmt.c.customer_id)
        .order_by(Customer.customer_id)
    )

    return json.dumps(
        [dict(r) for r in db.session.execute(result)], default=alchemyencoder
    )
```

 
```python
@bp.route("/price", methods=("GET", "POST"))
def totalRevenues_from_PGrated_movies_acto_nameStarts_with_S():

    actors_s = (
        db.session.query(Actor.actor_id, Actor.first_name, Actor.last_name)
        .filter(Actor.last_name.like("S%"))
        .subquery()
    )

    film_filmactor = (
        db.session.query(actors_s, Film.film_id, Film.title)
        .join(FilmActor, actors_s.c.actor_id == FilmActor.actor_id)
        .join(Film, Film.film_id == FilmActor.film_id)
        .filter(Film.rating == "PG")
        .subquery()
    )

    inventory_rental = (
        db.session.query(
            film_filmactor.c.first_name, film_filmactor.c.last_name, Payment.amount
        )
        .join(Inventory, Inventory.film_id == film_filmactor.c.film_id)
        .join(Rental, Inventory.inventory_id == Rental.inventory_id)
        .join(Payment, Rental.rental_id == Payment.rental_id)
    ).subquery()

    spg_rev = inventory_rental.alias("spg")
    final_query = (
        db.session.query(
            spg_rev.c.first_name,
            spg_rev.c.last_name,
            db.func.sum(spg_rev.c.amount).label("tot_revenue"),
        )
        .group_by(spg_rev.c.first_name, spg_rev.c.last_name)
        .order_by(db.func.sum(spg_rev.c.amount).desc())
    )
    return json.dumps(
        [dict(r) for r in db.session.execute(final_query)], default=alchemyencoder
    )

```

Output:
Run the following curl command on your terminal
```shell
$ curl -i http://localhost:5000/price
$ curl -i http://localhost:5000/info

```
Output:
```shell

[{"first_name": "NICK", "last_name": "STALLONE", "tot_revenue": 692.21}, {"first_name": "JEFF", "last_name": "SILVERSTONE", "tot_revenue": 652.35}, {"first_name": "DAN", "last_name": "STREEP", "tot_revenue": 509.02}, {"first_name": "GROUCHO", "last_name": "SINATRA", "tot_revenue": 457.97}, {"first_name": "SISSY", "last_name": "SOBIESKI", "tot_revenue": 379.03}, {"first_name": "JAYNE", "last_name": "SILVERSTONE", "tot_revenue": 372.18}, {"first_name": "CAMERON", "last_name": "STREEP", "tot_revenue": 361.0}, {"first_name": "JOHN", "last_name": "SUVARI", "tot_revenue": 296.36}, {"first_name": "JOE", "last_name": "SWANK", "tot_revenue": 177.52}]% 
```
```shell
[{"first_name": "MARY", "last_name": "SMITH", "num_rentals": 32, "tot_payments": 118.68}, {"first_name": "PATRICIA", "last_name": "JOHNSON", "num_rentals": 27, "tot_payments": 128.73}, {"first_name": "LINDA", "last_name": "WILLIAMS", "num_rentals": 26, "tot_payments": 135.74}, {"first_name": "BARBARA", "last_name": "JONES", "num_rentals": 22, "tot_payments": 81.78}, {"first_name": "ELIZABETH", "last_name": "BROWN", "num_rentals": 38, "tot_payments": 144.62}, {"first_name": "JENNIFER", "last_name": "DAVIS", "num_rentals": 28, "tot_payments": 93.72}, {"first_name": "MARIA", "last_name": "MILLER", "num_rentals": 33, "tot_payments": 151.67}, {"first_name": "SUSAN", "last_name": "WILSON", "num_rentals": 24, "tot_payments": 92.76}, {"first_name": "MARGARET", "last_name": "MOORE", "num_rentals": 23, "tot_payments": 89.77}, {"first_name": "DOROTHY", "last_name": "TAYLOR", "num_rentals": 25, "tot_payments": 99.75}, 
..................
```



Feedbacks are welcomed on how to optimize the queries , you can make a pull request to update it.
There are more examples available here [Learning SQL by Alan Beaulieu] (https://www.amazon.com/Learning-SQL-Master-Fundamentals/dp/0596520832), you can always try.

### References
1. [SQLALchemy ORM docs](https://docs.sqlalchemy.org/en/13/orm/query.html)


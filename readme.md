# Django, GeoDjango and STAC

This repository contains materials used and showcased in the DjangoCon Africa 2025.The talk is/was about
how to use the Django framework to build a STAC API implementing the [STAC](https://stacspec.org/) standard.


The repository includes the Django project that implements a STAC API.



## Getting Started

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/samweli/djangocon_africa_2025.git
   cd djangocon_africa_2025/
   ```

2. **Setup Database**
   #### PostgreSQL
__________

Install and start PostgreSQL by running:

 ```bash
 sudo apt update
 sudo apt install postgresql postgresql-contrib libpq-dev
 sudo service postgresql start
```


After installing PostgreSQL, you'll need to initialize the database.

1.  Log in as the admin user:

    ```bash
    sudo su -l postgres
    ```

2.  Create the project database:

    ```bash
    createdb stac
    ```

3.  Connect to the database shell:

    ```bash
    psql stac
    ```

4.  Grant privileges and enable the PostGIS extension:

    ```sql
    CREATE USER stac WITH PASSWORD 'stac';
    GRANT ALL PRIVILEGES ON DATABASE stac TO stac;
    CREATE EXTENSION postgis;
    exit;
    ```

3. **Create virtual environment**

```bash
  mkvirtualenv stac_api
```
4. **Update migrations**

   ```bash
      pip install -r requirements.txt
   ```

   ```bash
     ./manage.py migrate
   ```

5. **Create test data**(optional)
   Use the scripts/asset_fetch.py script to create sample test data.

   ```bash
   pip install -r scripts/requirements.txt
   ```

   Then run the script to create test data

   ```bash  
    python scripts/asset_fetch.py
    ```

    After the scripts finishes. A download directory and a GeoJson file will be created in the scripts folder.
    Use the GeoJson file content to populate the database using .


6. **Start and run the Django Project**
   
   ```bash
     ./manage.py runserver
   ```
7. Once the project is running, you'll see a URL in the console output. It will look something like:
    ```bash 
      http://127.0.0.1:8000
    ```
8. Open this URL in your web browser. You'll be taken to the STAC API implementation.


## Resources 

### Contributing
Feel free to contribute to the project by submitting pull requests or issues on GitHub.


### License
This project is licensed under the MIT License. See the LICENSE file for more details.

### Contact
If you have any questions or issues, please reach out smwltwesa6@gmail.com
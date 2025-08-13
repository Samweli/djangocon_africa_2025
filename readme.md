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


Create a database and user:

    ```bash
    sudo su -l postgres
  
    createdb stac
    
    psql stac
    ```

Grant privileges to the user

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

Copy the `.env.example` file to `.env` and 
edit the file and update the database credentials.


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

    After the scripts finishes a `downloads` directory and a geojson file will be created in the scripts folder.
    Use the geojson file content to populate the database using the following command.

    ```bash
      ./manage.py shell < import_landsat.py
    ```

    Following output should be displayed in the console if the data was imported successfully.

    ```bash
    Imported item: LC08_L2SP_047027_20200729_02_T1
      → Asset added for LC08_L2SP_047027_20200729_02_T1
    Imported item: LC08_L2SP_046027_20200722_02_T1
      → Asset added for LC08_L2SP_046027_20200722_02_T1
    Imported item: LC08_L2SP_047027_20200713_02_T1
      → Asset added for LC08_L2SP_047027_20200713_02_T1
    Imported item: LC08_L2SP_046027_20200706_02_T1
      → Asset added for LC08_L2SP_046027_20200706_02_T1
    ```

6. **Start and run the Django Project**
   
   ```bash
     ./manage.py runserver
   ```
7. Once the project is running, you'll see a URL in the console output. It will look something like:
    ```bash 
      http://127.0.0.1:8000
    ```
8. Open this URL in your web browser and head over `http://127.0.0.1:8000/stac`, You'll be taken to the STAC API Catalog root page..


## Resources 

### Contributing
Feel free to contribute to the project by submitting pull requests or issues on GitHub.


### License
This project is licensed under the MIT License. See the LICENSE file for more details.

### Contact
If you have any questions or issues, please reach out smwltwesa6@gmail.com
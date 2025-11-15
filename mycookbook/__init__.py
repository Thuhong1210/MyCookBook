import os
from flask import Flask
import mysql.connector
from mysql.connector import pooling

# Load env if exists
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

# --------------------------
# MYSQL CONFIG – XAMPP
# --------------------------
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""      # default empty for XAMPP
app.config["MYSQL_DATABASE"] = "MyCookBook"
app.config["SECRET_KEY"] = "secret123"

# --------------------------
# MYSQL CONNECTION POOL
# --------------------------
db = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=10,
    host=app.config["MYSQL_HOST"],
    user=app.config["MYSQL_USER"],
    password=app.config["MYSQL_PASSWORD"],
    database=app.config["MYSQL_DATABASE"]
)

# --------------------------
# IMPORT ROUTES (must be last)
# --------------------------
from mycookbook import routes

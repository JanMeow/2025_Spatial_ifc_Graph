from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String

# =========================================================================================
"""
Currently, I am saving the data in a local excel file and read it from the file.
I will use SQLAlchemy to connect to the database and save the data to the database.
All products and build Data ideally should be requested through the platform API. 
But for the bauteil matacher, another DB should be set up to store the representative products for easier search.
The represnetation is determined based on either ML learned or data exploration.
Currently, I am using the data exploration to determine the representative products.
u-value: Certain layer affect more than others 
acoustics: unknown
fire resistance: unknown
"""
# =========================================================================================
#  Database Connection
# =========================================================================================
# engine = create_engine("sqlite:///database.db")
engine = create_engine("postgres+psycopg2://postgres:postgres@localhost:5432/buildups")
meta = MetaData()
buildups = Table(
    "buildups",
    meta,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("description", String),
)

meta.create_all(engine)
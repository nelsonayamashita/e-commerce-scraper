from dotenv import load_dotenv
import sqlalchemy as db
import pandas as pd
import os 
from scrapers import submarino_scrape, amazon_scrape, petlove_scrape, petz_scrape, magalu_scrape, meli_scrape

def main():
    # Extract
    print("\nStart scraping Submarino...")
    submarino_products = submarino_scrape()
    print("\nStart scraping Amazon...")
    amazon_products = amazon_scrape()
    print("\nStart scraping Petlove...")
    petlove_products = petlove_scrape()
    print("\nStart scraping Petz...")
    petz_products = petz_scrape()
    print("\nStart scraping Magalu...")
    magalu_products = magalu_scrape()
    print("\nStart scraping Meli...")
    meli_products = meli_scrape()

    # Transform
    df_submarino = pd.DataFrame(submarino_products, columns=["name", "price", "old_price", "ratings"])
    df_submarino["e-commerce"] = "Submarino"

    df_amazon = pd.DataFrame(amazon_products, columns=["name", "price", "old_price", "ratings"])
    df_amazon["e-commerce"] = "Amazon"

    df_petz = pd.DataFrame(petz_products, columns=["name", "price", "old_price", "ratings"])
    df_petz["e-commerce"] = "Petz"

    df_petlove = pd.DataFrame(petlove_products, columns=["name", "price", "old_price", "ratings"])
    df_petlove["e-commerce"] = "Petlove"

    df_magalu = pd.DataFrame(magalu_products, columns=["name", "price", "old_price", "ratings"])
    df_magalu["e-commerce"] = "Magalu"

    df_meli = pd.DataFrame(meli_products, columns=["name", "price", "old_price", "ratings"])
    df_meli["e-commerce"] = "Mercado Livre"

    df = pd.DataFrame()
    for df0 in [df_submarino, df_amazon, df_petz,  df_petlove, df_magalu, df_meli]:
        df = pd.concat([df, sanitize(df0)])

    df["discount"] = (1 - df['price']/df['old_price']) * 100
    
    # Load

    # Assumes you created an user and a password, a database and has granted
    # schema privileges to the user (or that user is the owner)
    load_dotenv() 
    USR = os.getenv("USR")
    PASSWORD = os.getenv("PASSWORD")
    print("\nLoading into database...")
    engine = db.create_engine(f"postgresql://{USR}:{PASSWORD}@localhost:5432/ecommerce")
    df.to_sql("scrape_results", engine, if_exists='replace', index=False)
    engine.dispose()
    print("\nDone!")


def string_to_float(value):
    if value != "NA" and value != "sem" and len(value):
        return float(value.replace("R$", "").replace(",", "."))
    else:
        return pd.NA


def sanitize(df):
    df_clean = df.copy()
    # Transform strings to floats
    df_clean["price"] = pd.to_numeric(df_clean["price"].apply(string_to_float))
    df_clean["old_price"] = pd.to_numeric(df_clean["old_price"].apply(string_to_float))
    df_clean["ratings"] = pd.to_numeric(df_clean["ratings"].apply(string_to_float))

    df_clean["name"] = df_clean["name"].str.lower()
    
    # Replace any character that is not a letter neither a digit
    df_clean["name"] = df_clean["name"].replace('[^a-zA-Z0-9\sáéíóúâêîôûàèìòùãõäëïöüçñ\,]', '', regex=True)

    # Standarize all numbers to have no space between them and the metric (eg: 15 kg -> 15kg)
    df_clean["name"] = df_clean["name"].replace(r'(\d+)\s*(kg|g)', r'\1\2', regex=True)

    # All NA ratings can be understood as having value 0 (no reviews)
    df_clean["ratings"] = df_clean["ratings"].fillna(0)
    
    df_clean = df_clean.drop_duplicates()
    return df_clean

if __name__ == "__main__":
    main()
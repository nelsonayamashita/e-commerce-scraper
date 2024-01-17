from scrappers import *

def string_to_float(value):
    if value != "NA" and value != "sem" and len(value):
        return float(value.replace("R$", "").replace(",", "."))
    else:
        return pd.NA

def sanitize(df):
    df_clean = df.copy()
    df_clean["price"] = df_clean["price"].apply(string_to_float)
    df_clean["old_price"] = df_clean["old_price"].apply(string_to_float)
    df_clean["ratings"] = df_clean["ratings"].apply(string_to_float)
    df_clean["name"] = df_clean["name"].str.lower()
    df_clean["name"] = df_clean["name"].replace('[^a-zA-Z0-9\sáéíóúâêîôûàèìòùãõäëïöüçñ\,]', '', regex=True)
    df_clean["name"] = df_clean["name"].replace(r'(\d+)\s*(kg|g)', r'\1\2', regex=True)
    df_clean = df_clean.drop_duplicates()
    return df_clean

submarino_products = submarino_scrape()
amazon_products = amazon_scrape()
petlove_products = petlove_scrape()
petz_products = petz_scrape()
magalu_products = magalu_scrape()

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

df = pd.DataFrame()
for df0 in [df_submarino, df_amazon, df_petz,  df_petlove, df_magalu]:
    df = pd.concat([df, sanitize(df0)])

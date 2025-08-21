from pathlib import Path
import os
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text
import numpy as np

#this function establishes the way we will talk with the db
def get_engine():
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    user = os.getenv("PGUSER", "postgres")
    passw = os.getenv("PGPASSWORD", "postgres")
    db = os.getenv("PGDATABASE", "dvdrental")
    return create_engine(f"postgresql+psycopg2://{user}:{passw}@{host}:{port}/{db}")

eng = get_engine() #establishing engine

#this function creates a kpi figure and saves it to the outpath 
def save_kpi(value, title, outpath): 
    outpath = Path(outpath)
    outpath.parent.mkdir(parents=True, exist_ok=True) #creates directory if not exists
    plt.figure(figsize=(6,3.5)) #creates the canvas 
    plt.axis("off")
    plt.text(0.5, 0.6, f"{value:,}",ha='center',va='center',fontsize=36)
    plt.text(0.5, 0.2, title, ha='center', va='center', fontsize=12)
    plt.tight_layout() #collapses all unnecessary whitespaces
    plt.savefig(outpath, dpi=160,bbox_inches='tight')
    plt.close()

def save_bar(df,x, y, title, outpath, step,rotate_x=0):
    outpath = Path(outpath)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(4,3.5))
    ymax = df[y].max()
    top = int(np.ceil(ymax/step)*step)
    plt.bar(df[x].astype(str), df[y]) 
    if rotate_x:
        plt.xticks(rotation=rotate_x, ha='right')
    plt.yticks(np.arange(0,top+step,step))
    plt.ylim(0,top)
    plt.title(title)
    plt.xlabel(x) #label on the x axis
    plt.ylabel(y) #the same but on the y
    plt.tight_layout()
    plt.savefig(outpath, dpi=160,bbox_inches='tight')
    plt.close()

def save_line(pivot_df, outpath, title):
    outpath = Path(outpath)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(9,4))
    for col in pivot_df.columns:
        plt.plot(pivot_df.index, pivot_df[col], label=str(col))
    plt.title(title)
    plt.xlabel("Month")
    plt.ylabel("Count")
    plt.legend(loc='best', fontsize=8)
    plt.tight_layout()
    plt.savefig(outpath, dpi=160, bbox_inches='tight')
    plt.close()

def save_heatmap(mat_df, title, outpath):
    outpath = Path(outpath)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8,4.5))
    plt.imshow(mat_df.values, aspect='auto')
    plt.xticks(range(mat_df.shape[1]), [str(c) for c in mat_df.columns], rotation=45, ha='right')
    plt.yticks(range(mat_df.shape[0]), [str(r) for r in mat_df.index])
    plt.title(title)
    plt.colorbar(orientation='vertical', shrink=0.8)
    plt.tight_layout()
    plt.savefig(outpath, dpi=160,bbox_inches='tight')
    plt.close()


def ecdf(x):
    x = np.sort(np.asarray(x))
    y = np.arange(1,len(x)+1)/len(x)
    return x,y


with eng.connect() as conn:
    df = pd.read_sql_query(text("SELECT 1 AS ok"), conn)
print(df)

OUT = Path("out/figs")
OUT.parent.mkdir(parents=True, exist_ok=True)

def total_num_of_actors_in_films():
    sql_number_of_actors_in_films = """
    WITH 
    actors_film_info AS (
        SELECT CONCAT(a.first_name, ' ', a.last_name) AS full_name,
            f.title,
            f.description,
            f.length
        FROM actor a
        JOIN film_actor fa
        ON a.actor_id = fa.actor_id
        JOIN film f
        ON f.film_id = fa.film_id)

    SELECT COUNT(*)
    FROM actors_film_info;
    """

    with eng.connect() as conn:
        df = pd.read_sql_query(text(sql_number_of_actors_in_films), conn)
    save_kpi(df.iloc[0,0], "Actor-Film rows", OUT/"Q1.png")


def num_of_films_greater60min():
    sql_greater60min = """
    WITH
    longer_than_60min AS (
    SELECT CONCAT(a.first_name, ' ', a.last_name) AS full_name,
        f.title
    FROM film f
    JOIN film_actor fa
    ON fa.film_id = f.film_id
    JOIN actor a
    ON a.actor_id = fa.actor_id
    WHERE length>60)

    SELECT COUNT(*)
    FROM longer_than_60min;
    """

    with eng.connect() as conn:
        df = pd.read_sql(text(sql_greater60min), conn)
    save_kpi(int(df.iloc[0,0]), "Films with duration more than 60 min",OUT/"Q2.png")

def top_actors_per_num_of_films():
    sql_max_actor = """
    SELECT a.actor_id,
        CONCAT(a.first_name, ' ', a.last_name) AS full_name,
        COUNT(*) AS cnt
    FROM actor a
    JOIN film_actor fa
    ON a.actor_id = fa.actor_id
    JOIN film f
    ON f.film_id = fa.film_id
    GROUP BY a.actor_id,full_name
    ORDER BY cnt DESC LIMIT 1;
    """

    with eng.connect() as conn:
        df = pd.read_sql(text(sql_max_actor), conn)
    title = f"Actor with the largest num of films: {df.iloc[0,1]}"
    save_kpi(int(df.iloc[0,2]), title, OUT/"Q3.png")

    sql_top_ten_actors = sql_max_actor.replace("LIMIT 1", "LIMIT 10")
    with eng.connect() as conn:
        df = pd.read_sql(text(sql_top_ten_actors), conn)
    save_bar(df,x='full_name', y='cnt',title="Top 10 actors with the largest num of films",outpath=OUT/'Q4.png', rotate_x=45, step=5)

def num_of_films_per_length_group():
    sql_filmlen_groups = """
    SELECT (CASE WHEN f.length<=60 THEN 1 
                WHEN f.length<=120 THEN 2
                WHEN f.length<=180 THEN 3
                ELSE 4 END) AS filmlen_groups,
            COUNT(*) AS films_in_a_group

    FROM film f
    GROUP BY filmlen_groups
    ORDER BY filmlen_groups;
    """
    with eng.connect() as conn:
        df = pd.read_sql(text(sql_filmlen_groups), conn)
    save_bar(df, x="filmlen_groups", y="films_in_a_group", title="Number of films per length group",outpath=OUT/'Q5.png',step=50)

def num_of_rentals_per_family_categories():
    sql_family_films_num_of_rentals = """
    WITH temp AS(
    SELECT f.title,
            c.name AS category,
            COUNT(r.rental_id) AS cnt
    FROM film f
    JOIN film_category fc
    ON f.film_id = fc.film_id
    JOIN category c
    ON c.category_id = fc.category_id 
    AND (c.name = 'Animation' OR c.name = 'Children' OR c.name = 'Classics' OR c.name = 'Comedy' 
    OR c.name = 'Family' OR c.name = 'Music')
    LEFT JOIN inventory i
    ON i.film_id = f.film_id
    LEFT JOIN rental r
    ON r.inventory_id = i.inventory_id
    GROUP BY f.film_id, c.name,f.title
    ORDER BY category, f.title)

    SELECT category,
       SUM(cnt) AS num_of_rentals
    FROM temp
    GROUP BY category
    ORDER BY num_of_rentals DESC
    """
    with eng.connect() as conn:
        df = pd.read_sql(text(sql_family_films_num_of_rentals), conn)
    save_bar(df, "category", "num_of_rentals", "Total number of film rentals per family category", OUT/"Q6.png",100, 45)

def family_films_duration_quartiles():
    sql_family_films_duration_quartiles = """
    WITH 
    quartile AS (
    SELECT c.name AS category,
            NTILE(4) OVER (ORDER BY f.rental_duration, f.film_id) AS percentile
    FROM film f
    JOIN film_category fc
        ON fc.film_id = f.film_id
    JOIN category c
        ON c.category_id = fc.category_id
    )

    SELECT q.category,
        q.percentile,
        COUNT(*) AS cnt
    FROM quartile q
    WHERE q.category IN ('Animation','Children','Classics','Comedy','Family','Music')
    GROUP BY q.category, q.percentile
    ORDER BY q.category, q.percentile
    """
    with eng.connect() as conn:
        df = pd.read_sql(text(sql_family_films_duration_quartiles), conn)

    fig,axs = plt.subplots(2,2,figsize=(10,6), sharey=True)
    axs = axs.ravel() #flattening 2D array to simplify looping below
    for i,q in enumerate([1,2,3,4]):
        sub = df[df['percentile'] == q]
        axs[i].bar(sub['category'],sub['cnt'])
        axs[i].set_title(f"Quartile {q}")
        axs[i].tick_params(axis='x',labelrotation=45)

    fig.supylabel("Count") #making a general lable, not for each graph, just on the left 
    fig.supxlabel("Category")#same here but at the bottom
    fig.suptitle("Family categories x rental-duration quartiles")
    fig.tight_layout()
    fig.savefig(OUT/'Q7.png', dpi=160, bbox_inches='tight')
    plt.close(fig)

def count_rentals_per_month_and_store():
    sql_count_rentals_per_month_and_store = """
    SELECT inv.store_id,
       DATE_TRUNC('month',r.rental_date) AS rental_month,
	   COUNT(*) AS Count_rentals
    FROM inventory inv
    JOIN rental r
    ON inv.inventory_id = r.inventory_id
    GROUP BY inv.store_id, DATE_TRUNC('month',r.rental_date)
    ORDER BY rental_month,inv.store_id 
    """
    with eng.connect() as conn:
        df = pd.read_sql(text(sql_count_rentals_per_month_and_store), conn)
    df['rental_month'] = pd.to_datetime(df['rental_month'])
    pivot = df.pivot_table(values='count_rentals', index='rental_month', columns='store_id', aggfunc='sum').fillna(0)
    fig, ax = plt.subplots(figsize=(10,5))
    cols = list(pivot.columns)
    x = np.arange(0,len(pivot.index))
    n = len(cols)
    width = 0.8/max(n,1)
    for i,col in enumerate(cols): #creates a dictionary with key values that correspond to the index of a column
        ax.bar(x-width+i*width+width/2,pivot[col].values,width, label=f"Store {col}")
    ax.set_xticks(x) #creates ticks at the corresponding positions of x
    ax.set_xticklabels(pivot.index.strftime("%Y-%m"), rotation=45, ha='center')#naming those ticks that we created

    ax.set_title("Monthly rentals per store")
    ax.set_xlabel("Month")
    ax.set_ylabel("Rentals count")
    ax.legend(loc='best',fontsize=8)
    ax.grid(axis="y", linestyle=":") #creates horizontal dotted lines

    fig.tight_layout()
    fig.savefig(OUT/'Q8.png', dpi=160, bbox_inches='tight')
    plt.close(fig)

def main():
    total_num_of_actors_in_films()
    num_of_films_greater60min()
    top_actors_per_num_of_films()
    num_of_films_per_length_group()
    num_of_rentals_per_family_categories()
    family_films_duration_quartiles()
    count_rentals_per_month_and_store()

main()



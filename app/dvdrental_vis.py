from pathlib import Path
import os
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text
import numpy as np
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from functools import lru_cache
from packages import *

def _assert_dvdrental_loaded(engine):
    with engine.connect() as conn:
        ok = conn.execute(text("""
            SELECT EXISTS (
              SELECT 1
              FROM information_schema.tables
              WHERE table_schema='public' AND table_name='film'
            )
        """)).scalar()
    if not ok:
        raise SystemExit(
            "dvdrental not loaded yet (missing table 'film'). "
            "Put dvdrental.tar into initdb/ and re-run the DB, or restore manually. "
            "Skipping plots."
        )

eng = get_engine() #establishing engine
_assert_dvdrental_loaded(eng)

#this function creates a kpi figure and saves it to the outpath 
def save_kpi(value, title, outpath): 
    """
    Render a simple KPI card (big number + subtitle) and save it as a PNG.

    Parameters
    ----------
    value : int | float | array-like of length 1
        Number to display. Arrays/Series/DataFrames must contain a single value.
    title : str
        Subtitle shown under the big number.
    outpath : str | pathlib.Path
        Destination file path. Parent folders are created if missing.
    """

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
    """
    Render a vertical bar chart from a DataFrame and save it as a PNG.

    Parameters
    ----------
    df : pandas.DataFrame
        Source table containing columns `x` and `y`.
    x : str
        Column name to use for category labels on the x-axis. Coerced to string.
    y : str
        Column name with numeric bar heights.
    title : str
        Plot title.
    outpath : str or pathlib.Path
        Destination file path. Parent directories are created if missing.
    step : int or float
        Spacing between major y-axis ticks (e.g., 5 gives 0,5,10,...).
    rotate_x : int, optional
        Degrees to rotate x tick labels (e.g., 45). Default is 0.

    Returns
    -------
    None
        Saves the figure to `outpath`.

    Raises
    ------
    KeyError
        If `x` or `y` is not a column in `df`.
    ValueError
        If `step <= 0` or if `y` cannot be interpreted as numeric.
    """

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
    """
    Plot a multi-line chart (one line per column) and save it as a PNG.

    Parameters
    ----------
    pivot_df : pandas.DataFrame
        Wide table where the index provides x-values (e.g., months) and each
        column is a separate series to plot as a line. Missing values are
        allowed; Matplotlib will gap the line at NaNs.
    outpath : str or pathlib.Path
        Destination file path for the PNG. Parent directories are created
        if they do not exist.
    title : str
        Plot title shown at the top.

    Returns
    -------
    None
        Writes the figure to `outpath`.
    """

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
    """
    Draw a heatmap from a 2D numeric DataFrame and save as a PNG.

    Parameters
    ----------
    mat_df : pandas.DataFrame
        2D table of numeric values. Index supplies y tick labels; columns supply x tick labels.
    title : str
        Plot title.
    outpath : str | pathlib.Path
        Destination path. Parent folders are created.
    """

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


def plot_stacked_monthly(df, title, ylabel, outpath):
    """
    Plot a stacked monthly column chart and save it as a PNG.

    Parameters
    ----------
    df : pandas.DataFrame
        Wide table where rows are months (DatetimeIndex or strings) and columns are
        series to stack (e.g., customer names). Values must be numeric (>= 0 makes
        stacking interpretable).
    title : str
        Figure title.
    ylabel : str
        Y-axis label.
    outpath : str or pathlib.Path
        Destination PNG path. Parent directories must exist (or be creatable).

    Returns
    -------
    None
        Writes the figure to `outpath`.
    """
    
    x = np.arange(len(df.index))
    bottoms = np.zeros(len(x))
    fig, ax = plt.subplots(figsize=(11,4.8))

    handles =[]
    for col in df.columns:
        bars = ax.bar(x,df[col].values,bottom=bottoms,label=str(col))#this creates a subbar for customer col for each month
        handles.append(bars[0])#we will pass this to the legend later, so we save first values of each instance of customer subbar
        bottoms += df[col].values #regulates the beginning position of the next subbar in each column
    
    ax.set_xticks(x)
    ax.set_xticklabels([d.strftime("%Y-%m") for d in df.index],rotation=45, ha='center')

    ax.set_title(title)
    ax.set_xlabel("Month")
    ax.set_ylabel(ylabel)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=6, integer=False))

    ax.legend(handles=handles, labels=[str(c) for c in df.columns])

    fig.tight_layout()
    fig.savefig(outpath, dpi=160,bbox_inches='tight')
    plt.close(fig)

with eng.connect() as conn:
    df = pd.read_sql_query(text("SELECT 1 AS ok"), conn)
print(df)
print("connection is successful")


def total_num_of_actors_in_films():
    """Finds the total number of actors that participated in films"""

    sql_number_of_actors_in_films = load_sql('q1.sql')

    with eng.connect() as conn:
        df = pd.read_sql_query(text(sql_number_of_actors_in_films), conn)
    save_kpi(df.iloc[0,0], "Actor-Film rows", OUT/"Q1.png")


def num_of_films_greater60min():
    """Finds the number of films that are greater than 60 minutes and saves to KPI"""

    sql_greater60min = load_sql('q2.sql')

    with eng.connect() as conn:
        df = pd.read_sql(text(sql_greater60min), conn)
    save_kpi(int(df.iloc[0,0]), "Films with duration more than 60 min",OUT/"Q2.png")

def top_actors_per_num_of_films():
    """
    Find the most prolific actor and the top-10 by film count; save a KPI and a bar chart.
    """

    sql_max_actor = load_sql('q3.sql')

    with eng.connect() as conn:
        df = pd.read_sql(text(sql_max_actor), conn)
    title = f"Actor with the largest num of films: {df.iloc[0,1]}"
    save_kpi(int(df.iloc[0,2]), title, OUT/"Q3.png")

    sql_top_ten_actors = sql_max_actor.replace("LIMIT 1", "LIMIT 10")
    with eng.connect() as conn:
        df = pd.read_sql(text(sql_top_ten_actors), conn)
    save_bar(df,x='full_name', y='cnt',title="Top 10 actors with the largest num of films",outpath=OUT/'Q4.png', rotate_x=45, step=5)

def num_of_films_per_length_group():
    """
    Count films by runtime bucket (≤60, 61–120, 121–180, >180 minutes) and save a bar chart.
    """

    sql_filmlen_groups = load_sql('q4.sql')
    with eng.connect() as conn:
        df = pd.read_sql(text(sql_filmlen_groups), conn)
    save_bar(df, x="filmlen_groups", y="films_in_a_group", title="Number of films per length group",outpath=OUT/'Q5.png',step=50)

def num_of_rentals_per_family_categories():
    """
    Plot total rental events per family film category and save as a PNG.

    Parameters
    ----------
    None

    Returns
    -------
    None
        Writes the figure to disk.

    Raises
    ------
    sqlalchemy.exc.SQLAlchemyError
        If the SQL query or connection fails.
    KeyError
        If expected columns are missing from the result.
    ValueError
        If the result is empty and cannot be plotted."""


    sql_family_films_num_of_rentals = load_sql('q5.sql')
    with eng.connect() as conn:
        df = pd.read_sql(text(sql_family_films_num_of_rentals), conn)
    save_bar(df, "category", "num_of_rentals", "Total number of film rentals per family category", OUT/"Q6.png",100, 45)

def family_films_duration_quartiles():
    """
    Visualize family categories across rental-duration quartiles (Q1–Q4) and save as PNG.

    Parameters
    ----------
    None

    Returns
    -------
    None
        Writes the figure to disk.

    Notes
    -----
    This counts **films** per category/quartile based on `film.rental_duration`. It does
    not count rental events. To visualize rentals instead, join through `inventory` and
    `rental` and aggregate on those tables.
    """

    sql_family_films_duration_quartiles = load_sql('q6.sql')
    with eng.connect() as conn:
        df = pd.read_sql(text(sql_family_films_duration_quartiles), conn)

    fig,axs = plt.subplots(2,2,figsize=(10,6), sharey=True)
    axs = axs.ravel() #flattening 2D array to simplify looping below
    for i,q in enumerate([1,2,3,4]):
        sub = df[df['percentile'] == q]
        axs[i].bar(sub['category'],sub['cnt'])
        axs[i].set_title(f"Quartile {q}")
        axs[i].tick_params(axis='x',labelrotation=45)

    fig.supylabel("Number of films rented") #making a general lable, not for each graph, just on the left 
    
    fig.suptitle("Number of family films rented per each quartile of rental duration")
    fig.tight_layout()
    fig.savefig(OUT/'Q7.png', dpi=160, bbox_inches='tight')
    plt.close(fig)

def count_rentals_per_month_and_store():
    """
    Draws a grouped bar chart of monthly rental counts per store and save as a PNG.

    Parameters
    ----------
    None

    Returns
    -------
    None
        Writes the figure to disk.

    Raises
    ------
    sqlalchemy.exc.SQLAlchemyError
        If the SQL query or connection fails.
    KeyError
        If expected columns are missing from the query result.
    ValueError
        If the result is empty and cannot be plotted."""


    sql_count_rentals_per_month_and_store = load_sql('q7.sql')

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

def top10customers_payment_total_per_month():
    """
    Computes top 10 customers by total payments, then summarize monthly amount and count.

    Returns
    -------
    None
        Saves figures into the `OUT` directory.

    Notes
    -----
    - If some months have no data, reindexing to a full month index ensures 0-valued rows so
      the charts show complete calendars.
    """

    sql_top10customers_payment_total_per_month = load_sql('q8.sql')
    with eng.connect() as conn:
        df = pd.read_sql(text(sql_top10customers_payment_total_per_month), conn)
    
    df["pay_mon"] = pd.to_datetime(df["pay_mon"])

    months = pd.date_range('2007-01-01','2007-12-31', freq='MS')#creating an aray of months
    amt = df.pivot_table(index='pay_mon', columns='full_name', values='pay_amount', aggfunc='sum').reindex(months).fillna(0)

    cnt = df.pivot_table(index='pay_mon', columns='full_name', values='pay_countpermon').reindex(months).fillna(0)

    order = amt.sum().sort_values(ascending=False).index.tolist()#calculates the total sum of each customer pay_amount and sorts in desc order
    amt = amt.reindex(columns = order)
    cnt = cnt.reindex(columns = order)
    
    plot_stacked_monthly(amt, title="Top 10 customers'(by total amount payed) monthly payment amount in 2007", ylabel='Payment amount', outpath=OUT/'Q9.png')
    plot_stacked_monthly(cnt, title="Top 10 customers'(by total amount payed) monthly count of payments in 2007",ylabel='Number of payments', outpath=OUT/'Q10.png')


def difference_across_monthly_payments():
    """
    Plots month-over-month payment changes for the top 10 customers (year 2007) and save as PNG.

    Parameters
    ----------
    None

    Returns
    -------
    None
        Writes the figure to disk.

    Raises
    ------
    sqlalchemy.exc.SQLAlchemyError
        If the database query fails or the connection cannot be established.
    KeyError
        If expected columns are missing from the query result.
    ValueError
        If the resulting DataFrame is empty after querying/pivoting.
    """


    sql_difference_across_monthly_payments = load_sql('q9.sql')

    with eng.connect() as conn:
        df = pd.read_sql_query(text(sql_difference_across_monthly_payments), conn)
    
    df['pay_mon'] = pd.to_datetime(df['pay_mon'])
    pivot = df.pivot_table(index='pay_mon', columns='full_name', values='monthly_diff_lag', aggfunc='sum').sort_index()

    idx=pd.date_range(pivot.index.min(), pivot.index.max(), freq='MS')
    pivot = pivot.reindex(idx)

    fig,ax = plt.subplots(figsize=(11,5))
    for col in pivot.columns:
        ax.plot(pivot.index, pivot[col], label=str(col))
    
    ax.axhline(0, linewidth=1, linestyle='--')#baseline at 0 to see negative changes

    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    fig.autofmt_xdate()

    ax.set_title("Monthly change in payment amount vs previous month for Top 10 customers by amount payed")
    ax.set_xlabel("Month")
    ax.set_ylabel("Month payment amount difference")
    ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), fontsize=8)
    ax.grid(axis='y', linestyle=':')

    fig.tight_layout(rect=[0, 0, 0.88, 1])
    fig.savefig(OUT / "Q11.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def main():
    total_num_of_actors_in_films()
    num_of_films_greater60min()
    top_actors_per_num_of_films()
    num_of_films_per_length_group()
    num_of_rentals_per_family_categories()
    family_films_duration_quartiles()
    count_rentals_per_month_and_store()
    top10customers_payment_total_per_month()
    difference_across_monthly_payments()

if __name__=='__main__':
    main()



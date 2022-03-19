import pandas as pd
import seaborn as sb
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp

gdp = pd.read_excel("./gdp_rankings.xlsx")
gdp = gdp[["Country","GDP \nper capita "]]
gdp["GDP \nper capita "] = gdp["GDP \nper capita "].str.replace("$", "").str.replace(",", "")
gdp.sort_values('GDP \nper capita ')
print(gdp)


deaths = pd.read_csv("./deaths_under_5_global.csv", header=4)

#make dataframe formatted for induvidual country time series data visualization & later data analysis
list_of_years = [ str(i) for i in[*range(1960, 2020, 1)] ]
deaths_t = deaths.T
deaths_3 = deaths_t.drop(deaths_t.index[1:4])
deaths_3.columns = deaths_3.iloc[0]
deaths_4 = deaths_3.drop(deaths_3.index[0])
deaths_4['Year'] = deaths_4.index
print(deaths_4)

#sb.lineplot(x="Year", y="Afghanistan", data=deaths_4)
#sb.lineplot(x="Year", y="Canada", data=deaths_4)
#sb.lineplot(x="Year", y="India", data=deaths_4)
#sb.lineplot(x="Year", y="Austria", data=deaths_4)
#plt.show()

#group countries into 3 groups: rich, middle, poor
countries_listed = deaths_4.columns
number_gdp_listed = len(gdp.index)
gdp_rich = gdp['Country'].iloc[:round(number_gdp_listed*1/3)].tolist()
gdp_middle = gdp['Country'].iloc[round(number_gdp_listed*1/3):round(number_gdp_listed*2/3)].tolist()
gdp_poor = gdp['Country'].iloc[round(number_gdp_listed*2/3):-1].tolist()

rich = []
middle = []
poor = []
for i in countries_listed:
    if i in gdp_rich:
        rich.append(i)
    elif i in gdp_middle:
        middle.append(i)
    elif i in gdp_poor:
        poor.append(i)

print(f"{len(rich+middle+poor)} countries remaining in all our lists")

# remove groups with missing values to ensure same data sizes
deaths_rich = deaths_4[rich].dropna(axis=1, how="any")
deaths_middle = deaths_4[middle].dropna(axis=1, how="any")
deaths_poor = deaths_4[poor].dropna(axis=1, how="any")

#add up the three groups' yearly totals
deaths_rich['total'] = deaths_rich.iloc[:, :].sum(axis=1)
deaths_middle['total'] = deaths_middle.iloc[:, :].sum(axis=1)
deaths_poor['total'] = deaths_poor.iloc[:, :].sum(axis=1)

#normalize data min-max
deaths_rich['total'] = (deaths_rich['total']-deaths_rich['total'].min())/(deaths_rich['total'].max()-deaths_rich['total'].min())
deaths_middle['total'] = (deaths_middle['total']-deaths_middle['total'].min())/(deaths_middle['total'].max()-deaths_middle['total'].min())
deaths_poor['total'] = (deaths_poor['total']-deaths_poor['total'].min())/(deaths_poor['total'].max()-deaths_poor['total'].min())
print(deaths_rich)

#plot the three graphs
total_df = pd.DataFrame().assign(rich=deaths_rich['total'], middle=deaths_middle['total'], poor=deaths_poor['total'], year=deaths_4['Year'])
total_df.reset_index(inplace=True)
total_df.drop(columns=['index'], inplace=True)
print(total_df)

# HAVE TO FIX THE NORMALIZTION; do ti earlier
graph_df = pd.melt(frame=total_df, id_vars=['year'], value_vars=['middle', 'rich', 'poor'], value_name="relative_deaths")
sb.lineplot(x="year", y="relative_deaths", hue="variable", data=graph_df)
plt.show()

#do ANOVA on the three groups

'''
RESULTS:

CONCLUSION: 

'''

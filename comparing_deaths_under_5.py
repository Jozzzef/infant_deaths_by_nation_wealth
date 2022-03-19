import pandas as pd
import seaborn as sb
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm

#from https://www.worldometers.info/gdp/gdp-by-country/
#this data ranks countries by their GDP
gdp = pd.read_excel("./gdp_rankings.xlsx")
gdp = gdp[["Country","GDP \nper capita "]]
gdp["GDP \nper capita "] = gdp["GDP \nper capita "].str.replace("$", "").str.replace(",", "")
gdp.sort_values('GDP \nper capita ')
print(gdp)

#from https://data.worldbank.org/indicator/SH.DTH.MORT
#this data has a list of deaths under the age of 5 for all countries by year starting in 1960 (although some have no or sparse data)
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
#divide yearly totals by how many countries sampled in their group
deaths_rich['total'] = deaths_rich.iloc[:, :].sum(axis=1)/len(deaths_rich)
deaths_middle['total'] = deaths_middle.iloc[:, :].sum(axis=1)/len(deaths_middle)
deaths_poor['total'] = deaths_poor.iloc[:, :].sum(axis=1)/len(deaths_poor)

#normalize totals
deaths_rich['total'] = (deaths_rich['total']-deaths_rich['total'].mean())/deaths_rich['total'].std()
deaths_middle['total'] = (deaths_middle['total']-deaths_middle['total'].mean())/deaths_middle['total'].std()
deaths_poor['total'] = (deaths_poor['total']-deaths_poor['total'].mean())/deaths_poor['total'].std()
print(deaths_rich)

#prepare for plotting on a line graph, then plot the three graphs
total_df = pd.DataFrame().assign(rich=deaths_rich['total'], middle=deaths_middle['total'], poor=deaths_poor['total'], year=deaths_4['Year'])
total_df.reset_index(inplace=True)
total_df.drop(columns=['index'], inplace=True)
print(total_df)

graph_df = pd.melt(frame=total_df, id_vars=['year'], value_vars=['middle', 'rich', 'poor'], value_name="relative_deaths")
sb.lineplot(x="year", y="relative_deaths", hue="variable", data=graph_df)
#plt.show()
graph_df["year"] = pd.to_numeric(graph_df["year"])
#linear models
sb.lmplot(x="year", y="relative_deaths", hue="variable", order=2, data=graph_df) 

#do ANOVA on the three groups
#samples clearly not normal, left skewed; 60 samples each; not independant because dependant on previous years, therefore time-series analysis needed;
#for simplicity's sake, let us compare the three linear models; they will inherently be significantly different since we have one data point for each year and because I saw the confidence intervals in the linear model plot which do not overlap therefore just take a quick peak at the model stats and call it a day

sb.displot(graph_df, x="relative_deaths", hue="variable")
#plt.show()

rel_rich = total_df['rich'].to_numpy()
rel_middle = total_df['middle'].to_numpy()
rel_poor = total_df['poor'].to_numpy()
year_list = pd.to_numeric(total_df["year"]).to_numpy()

poisson_model_rich = sm.GLM(year_list, rel_rich, family=sm.families.Poisson())
results_rich = poisson_model_rich.fit()
print(results_rich.summary())

poisson_model_middle = sm.GLM(year_list, rel_middle, family=sm.families.Poisson())
results_middle = poisson_model_middle.fit()
print(results_middle.summary())

poisson_model_poor = sm.GLM(year_list, rel_poor, family=sm.families.Poisson())
results_poor = poisson_model_poor.fit()
print(results_poor.summary())

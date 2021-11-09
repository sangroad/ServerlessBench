import numpy as np
import matplotlib.pyplot as plt
import scipy
import seaborn as sns

filename = "possibleIATs.csv"
f = open(filename, "r")
f.readline()

data = []

for line in f:
    data.append(float(line[:-1]))

N = len(data)
x = np.sort(data)
y = np.arange(N) / float(N)

plt.xlabel('x-axis')
plt.ylabel('y-axis')
plt.title('CDF of IAT')
plt.plot(x, y)

#norm_cdf = scipy.stats.norm.cdf(data)
#kwargs = {'cumulative': True}
#sns.distplot(norm_cdf, hist_kws=kwargs, kde_kws=kwargs)
#sns.lineplot(x=data, y=norm_cdf)
plt.show()

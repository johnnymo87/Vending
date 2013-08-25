import operator

records = {}
with open('record_count_customers.txt', 'r') as f:
    for line in f:
        line = line.strip().split('\t')
        records[line[0]] = int(line[1])

records = sorted(records.iteritems(), key=operator.itemgetter(1))


import pylab as p
fig = p.figure()
ax = fig.add_subplot(1,1,1)
 
# I start by only supplying y data.
y = [r[1] for r in records]
 
# Calculate how many bars there will be
N = len(y)
 
# Generate a list of numbers, from 0 to N
# This will serve as the (arbitrary) x-axis, which
# we will then re-label manually.
ind = range(N)
 
# See note below on the breakdown of this command
ax.bar(ind, y, facecolor='#777777', 
       align='center', ecolor='black')
 
#Create a y label
ax.set_ylabel('Vends')
 
# Create a title, in italics
ax.set_title('Vends over the last 100 days, by customer',fontstyle='italic')
 
# This sets the ticks on the x axis to be exactly where we put
# the center of the bars.
ax.set_xticks(ind)
 
# Labels for the ticks on the x axis.  It needs to be the same length
# as y (one label for each bar)
group_labels = [r[0] for r in records]
 
# Set the x tick labels to the group_labels defined above.
ax.set_xticklabels(group_labels)
 
# Extremely nice function to auto-rotate the x axis labels.
# It was made for dates (hence the name) but it works
# for any long x tick labels
fig.autofmt_xdate()

fig.set_size_inches(48,12)
##p.show() 
p.savefig('vends_by_customer.png')


def pairs(lst):
    i = iter(lst)
    prev = item = i.next()
    for item in i:
        yield prev, item
        prev = item

def records_splitter(records, spreads):
    splits = [[] for spread in spreads]
    i = 0
    for spread in spreads:
        for j in range(spread[0], spread[1]):
            splits[i].append(records[j])
        i += 1
    return splits

def graphs(rank, records):
    fig = p.figure(figsize=(24,12))
    ax = fig.add_subplot(1,1,1)
    y = [r[1] for r in records]
    N = len(y)
    ind = range(N)
    ax.bar(ind, y, facecolor='#777777', 
           align='center', ecolor='black')
    ax.set_ylabel('Vends')
    ax.set_title('Vends over the last 100 days, by customer',fontstyle='italic')
    ax.set_xticks(ind)
    group_labels = [r[0] for r in records]
    ax.set_xticklabels(group_labels)
    fig.autofmt_xdate()
    p.savefig('Q{}_vends_by_customer.png'.format(i))

##step = len(records)/4
##quartiles = [step * quartile for quartile in range(4)]
##quartiles.append(len(records))
##quartiles = list(pairs(quartiles))
##quartiles = records_splitter(records, quartiles)
##
##i = 0
##for Q in quartiles:
##    i += 1
##    graphs(i, Q)


        
    




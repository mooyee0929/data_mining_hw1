"""
Description     : Simple Python implementation of the Apriori Algorithm
Modified from:  https://github.com/asaini/Apriori
Usage:
    $python apriori.py -f DATASET.csv -s minSupport

    $python apriori.py -f DATASET.csv -s 0.15
"""

import sys
import time
from itertools import chain, combinations
from collections import defaultdict
from optparse import OptionParser


def subsets(arr):
    """ Returns non empty subsets of arr"""
    return chain(*[combinations(arr, i + 1) for i, a in enumerate(arr)])


def returnItemsWithMinSupport(itemSet, transactionList, minSupport, freqSet):
    """calculates the support for items in the itemSet and returns a subset
    of the itemSet each of whose elements satisfies the minimum support"""
    _itemSet = set()
    localSet = defaultdict(int)
    
    for item in itemSet:
        for transaction in transactionList:
            if item.issubset(transaction):
                freqSet[item] += 1
                localSet[item] += 1

    for item, count in localSet.items():
        support = float(count) / len(transactionList)

        if support >= minSupport:
            _itemSet.add(item)

    return _itemSet

def returnCloesedItemsWithMinSupport(itemSet, superSet,minSupport,freqSet):
    """calculate the subset and check the support of each set """
    for supset in superSet:
        for item in itemSet:
            if item.issubset(supset) and freqSet[item] <= freqSet[supset]:
                itemSet.remove(item)
                break
    # print(itemSet)
    return itemSet
    


# 得到itemset的組合
def joinSet(itemSet, length):
    """Join a set with itself and returns the n-element itemsets"""
    return set(
        [i.union(j) for i in itemSet for j in itemSet if len(i.union(j)) == length]
    )


def getItemSetTransactionList(data_iterator):
    transactionList = list()
    itemSet = set()
    for record in data_iterator:
        transaction = frozenset(record)
        transactionList.append(transaction)
        for item in transaction:
            itemSet.add(frozenset([item]))  # Generate 1-itemSets
    return itemSet, transactionList


def runApriori(data_iter, minSupport, closed):
    """
    run the apriori algorithm. data_iter is a record iterator
    Return both:
     - items (tuple, support)
    """

    start_time = time.time()
    itemSet, transactionList = getItemSetTransactionList(data_iter)

    freqSet = defaultdict(int)
    largeSet = dict()
    closeSet = dict()
    # Global dictionary which stores (key=n-itemSets,value=support)
    # which satisfy minSupport
    
    oneCSet= returnItemsWithMinSupport(itemSet, transactionList, minSupport, freqSet)

    currentLSet = oneCSet
    count = len(currentLSet)
    closecount = 0
    k = 2
    while currentLSet != set([]):    
        largeSet[k - 1] = currentLSet
        currentCSet = joinSet(currentLSet, k)
        
        currentCSet= returnItemsWithMinSupport(
            currentCSet, transactionList, minSupport, freqSet
        )
        if closed:
            closeSet[k-1] = returnCloesedItemsWithMinSupport(currentLSet,currentCSet,minSupport,freqSet)
            closecount += len(closeSet)
        
        currentLSet = currentCSet
        count += len(currentLSet)
        
        k = k + 1

    end_time = time.time()
    # print('execution time :',end_time-start_time)
    def getSupport(item):
        """local function which Returns the support of an item"""
        return float(freqSet[item]) / len(transactionList)
    
    if not closed:
        f = open('statistics_file.txt',"w")
        f.write(str(count)+'\n')
        toRetItems = []
        out = ""
        for key, value in largeSet.items():
            toRetItems.extend([(set(item), getSupport(item)) for item in value])
            if key < len(largeSet):
                out += str(key) + '\t' + str(len(largeSet[key])) + '\t' + str(len(largeSet[key+1])) + '\n'
                # print(str(key) + '\t' + str(len(largeSet[key])) + '\t' + str(len(largeSet[key+1])))
            else:
                out += str(key) + '\t' + str(len(largeSet[key])) + '\t' + str(0) + '\n'
                # print(str(key) + '\t' + str(len(largeSet[k])) + '\t' + str(0))
        f.write(out)
        f.close()
        savetxt(toRetItems)
    else:
        f = open('closed_itemset_list.txt',"w")
        f.write(str(closecount)+'\n')
        toRetItems = []
        for key, value in closeSet.items(): 
            toRetItems.extend([(set(item), getSupport(item)) for item in value])
        out = ""
        for item, support in sorted(toRetItems, key=lambda x: x[1],reverse=True):
            out +=str(round(support*100,1))+'\t'+str(item)+'\n'
        f.write(out)
        f.close()
    
    return toRetItems


def printResults(items):
    """prints the generated itemsets sorted by support """
    for item, support in sorted(items, key=lambda x: x[1],reverse=True):
        print("item: %s , %.3f" % (str(item), support))

def savetxt(items):
    f = open('apriori_itemset_list.txt',"w")
    """prints the generated itemsets sorted by support """
    out = ""
    for item, support in sorted(items, key=lambda x: x[1],reverse=True):
        out += str(round(support*100,1))+'\t'+str(item)+'\n'
    f.write(out)
    f.close()


def dataFromFile(fname):
    """Function which reads from the file and yields a generator"""
    with open(fname, "r") as file_iter:
        for line in file_iter:
            line = line.strip().rstrip(" ")  # Remove trailing comma
            line = line.split(" ")[3:]
            line = [eval(i) for i in line]
            record = frozenset(line)
            yield record


if __name__ == "__main__":

    optparser = OptionParser()
    optparser.add_option(
        "-f", "--inputFile", dest="input", help="filename containing data", default='A.data'
    )
    optparser.add_option(
        "-s",
        "--minSupport",
        dest="minS",
        help="minimum support value",
        default=0.01,
        type="float",
    )

    optparser.add_option(
        "-c",
        "--closed",
        action="store_true",
        dest="closed",
        help="determine do task 2 or not",
        default=False
    )
    
    (options, args) = optparser.parse_args()

    inFile = None
    if options.input is None:
        inFile = sys.stdin
    elif options.input is not None:
        inFile = dataFromFile(options.input)
    else:
        print("No dataset filename specified, system with exit\n")
        sys.exit("System will exit")

    minSupport = options.minS
    closed = options.closed

    items = runApriori(inFile, minSupport,closed)

    #printResults(items)

    
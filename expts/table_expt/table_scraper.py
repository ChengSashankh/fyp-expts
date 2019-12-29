import os

########### Creating the data set from papers ###########

####### Display match statistics #######
def get_match_count(dirPath, queryString):
    count_list = []
    error_count = 0
    total_docs = 0
    # hits = []
    for f in os.listdir(dirPath):
        total_docs += 1
        ptr = open(os.path.join(dirPath, f))
        
        lines = []
        try:
            lines = ptr.readlines()
        except:
            error_count += 1
            continue
        
        count = 0
        for line in lines:
            if queryString in line:
                count += 1
                # hits.append(line)
        
        count_list.append(count)
    
    print ('Total number of documents: ' + str(total_docs))
    print ('Number of document matches: ' + str(sum(x != 0 for x in count_list)))
    print ('Total number of candidate equations: ' + str(sum(count_list)))
    print ('Error documents skipped: ' + str(error_count))
    
    # return hits

####### Collect text between query phrases #######
# Issue 1 resolved: Start and end in one line => missed
def get_matching_texts(dirPath, queryStringStart, queryStringEnd):
    results = []
    contexts = []
    error_count = 0
    for f in os.listdir(dirPath):
        ptr = open(os.path.join(dirPath, f))

        lines = []
        try:
            lines = ptr.readlines()
        except:
            error_count += 1
            continue

        started = False
        startedAt = 0
        snippet = ''

        for i, line in enumerate(lines):
            if not started:
                if queryStringStart in line:
                    started = True
                    startedAt = i
                    snippet = snippet + line

            if started:
                if startedAt != i:
                    snippet = snippet + line

                if queryStringEnd in line:
                    started = False
                    snippet = snippet + line
                    results.append(snippet)
                    contexts.append('\n'.join(lines[max(0, startedAt - 5) : min(len(lines), i + 6)]))
                    snippet = ''
    
    # print ('Total number of candidate equations: ' + str(sum(count_list)))
    print ('Error documents skipped: ' + str(error_count))
    return results, contexts


####### Run over a collection of start and end query strings #######
def aggregateResults(queryPairs, dirPath):
    res = []
    con = []

    for qp in queryPairs:
        results, contexts = get_matching_texts(dirPath, qp[0], qp[1])
        res.append(results)
        con.append(contexts)
    
    return res, con

def writeResultsToFile(matches, contexts, outfile):
    ptr = open(outfile, 'a')
    count = 0
    for match, context in zip(matches, contexts):
        ptr.write('\n[start-of-eqn]\n\n')
        ptr.write(match)
        ptr.write('\n[end-of-eqn]\n\n')
        ptr.write('\n[start-of-con]\n\n')
        ptr.write(context)
        ptr.write('\n[end-of-con]\n\n')
    ptr.close() 

# print (get_match_count('/Users/cksash/Documents/proj/FYP/expt1/data/papers/1998', '\\begin{eqnarray}'))
# matches, contexts = get_matching_texts('/Users/cksash/Documents/proj/FYP/expt1/data/papers/1998', '\\begin{eqnarray}', '\\end{eqnarray}')
# writeResultsToFile(matches, contexts, 'equations_with_con.txt')

# queryPairs = [['\\begin{eqnarray}', '\\end{eqnarray}'], ['\\begin{equation}', '\\begin{equation}']]
queryPairs = [['\\begin{table}', '\\end{table}']]
dataPath = '/home/cksash/Documents/data/readonly/unpacked'

dbr = 0
for qp in queryPairs:
    print (qp)
    for d in os.listdir(dataPath):
        print (d)
        if not os.path.isdir(os.path.join(dataPath, d)):
            continue
        matches, contexts = get_matching_texts(os.path.join(dataPath, d), qp[0], qp[1])
        writeResultsToFile(matches, contexts, './agg_eqn_match_2.txt')

# To use this script:
# Execute script
# Execute command "python manage.py loaddata matchings.json" from cmd in this directory

import sqlite3
from os import listdir
from os.path import isfile, join
import json
import collections

def main():
    ## Locate all allocation files
    mypath = "./allocations_data"
    folders = [f for f in listdir(mypath) if not isfile(join(mypath, f))]
    #onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    onlyfiles = []
    for folder in folders:
        folderpath = join(mypath, folder)
        #print(listdir(folderpath))
        for f in listdir(folderpath):
            filehandle = join(folderpath, f)
            if isfile(filehandle):
                onlyfiles.append(filehandle)
        #print([f for f in listdir(folderpath) if isfile(join(folderpath, f))])
    result = []
    pkindex = 0
    all_correct = True
    latex_comparison= open("comparison.txt", 'w')

    ## Read in allocations from files
    for filehandle in onlyfiles:
        filename = filehandle[filehandle.rindex("\\")+1:]
        print("Loading data from: "+filename)
        pkindex = pkindex+1 #allocation index
        #file = open(mypath+"/"+filename, 'r')
        file = open(filehandle, 'r')
        text = "".join(file.readlines()).replace("\n","")
        matching = json.loads(text) #convert to JSON to store in database
        num_rounds = len(matching) 
        #print(num_rounds)
        expected_participants = filename.split("_")[1]
        expected_group_sizes = filename.split("(")[1].split(")")[0].split(",")
        #print(num_participants)
        if not is_correct(matching, expected_participants, expected_group_sizes,latex_comparison):
            print("Error for matching in {0}".format(filename))
            all_correct = False
            #break
        #num_participants=0
        #for group in matching[0]:
            #for participant in group:
                #num_participants +=1
        result.append({
        "model":"groupings.allocation",
        "pk":pkindex,
        "fields":{
          "num_participants":expected_participants,
          "num_rounds":num_rounds,
          "matching":str(matching)
        }})
        file.close()
        #print("v={0:6s} k={1:6s} r={2:<6d}".format(expected_participants,",".join(expected_group_sizes),num_rounds))
        latex_comparison.write("{0:s}&{1:s}&{2:d}\n".format(expected_participants,",".join(expected_group_sizes),num_rounds))

    # ADD CORRECTNESS CHECK

    file = open("matchings.json", "w")
    json.dump(result, file)
    file.close()
    latex_comparison.close()
    print ("done")
    if all_correct:
        print("Success!")
    else:
        print("Failures found")


def is_correct(matching, expected_participants, expected_group_sizes,latex_comparison):
    ## Find number or participants
    num_participants=0
    for group in matching[0]:
        for participant in group:
            num_participants +=1
    if str(num_participants) != expected_participants:
        print("participants are {0} instead of {1}".format(num_participants, expected_participants))
        return False
    ## Check that blocks are correct
    for participant in range(num_participants):
        # checks whether participant appears exactly once each round
        matched_with = []
        for roundd in matching:
            present = False
            for group in roundd:
                if participant in group:
                    for member in group:
                        if member != participant:
                            matched_with.append(member)
                    if not present:
                        present = True
                    else:
                        print("Participant {0} appears more than once!".format(participant))
                        return False
            if not present:
                print("Participant {0} does not appear in every round!".format(participant))
                return False
        # checks whether a participant is matched with someone more than once (0 times is okay)
        counts = collections.Counter(matched_with)
        duplicates = [i for i in counts if counts[i]>1]
        if len(duplicates)>0:
            print("Participant {0} is matched with {1} more than once!".format(participant, duplicates))
            return False
    # check that group sizes differ by at most one
    group_sizes = []
    for roundd in matching:
        for group in roundd:
            size = str(len(group))
            if size not in group_sizes:
                group_sizes.append(size)
    if len(group_sizes)>2:
        print("Too many group sizes: {0}".format(group_sizes))
        return False
    if len(group_sizes)==2 and abs(int(group_sizes[0]) - int(group_sizes[1])) != 1:
        print("Group sizes differ by more than 1: {0} and {1}".format(group_sizes[0], group_sizes[1]))
    # check that the group sizes are the same as the ones advertised
    for size in group_sizes:
        if size not in expected_group_sizes:
            print("Group sizes are not as advertised: have {0}, expected {1}".format(group_sizes, expected_group_sizes))
            return False
    for size in expected_group_sizes:
        if size not in group_sizes:
            print("Group sizes are not as advertised: have {0}, expected {1}".format(group_sizes, expected_group_sizes))
            return False

    ## Find the two group sizes and the number of each group; and check that they are consistent for reach round
    t_size1, t_num1, t_size2, t_num2 = 0, 0, 0, 0
    for roundd in matching:
        size1, num1, size2, num2 = 0, 0, 0, 0
        for group in roundd:
            if len(group) != size1 and size1 == 0:
                size1 = len(group)
                num1 +=1
            elif len(group) != size1 and size1 != 0:
                if len(group) != size2 and size2 == 0:
                    size2 = len(group)
                    num2 += 1
                elif len(group) != size2 and size2 != 0:
                    pass
                elif len(group) == size2:
                    num2 += 1
            elif len(group) == size1:
                num1 += 1
        if t_size1 == 0:
            t_size1 = size1
            t_num1 = num1
            t_size2 = size2
            t_num2 = num2
        else:
            if t_size1 == size1:
                if t_num1 != num1:
                    print("Error occurrences of groups differ here: tsize1={0}, tnum1= {1}, size1= {2}, num1={3}".format(t_size1, t_num1, size1, num1))
                    return False
            elif t_size1 == size2:
                if t_num1 != num2:
                    print("Error occurrences of groups differ here: tsize1={0}, tnum1= {1}, size2= {2}, num2={3}".format(t_size1, t_num1, size2, num2))
                    return False
            else:
                print("Error occurrences of groups differ here- This error case shouldn't happen")
                return False
            if t_size2 == size1:
                if t_num2 != num1:
                    print("Error occurrences of groups differ here: tsize2={0}, tnum2= {1}, size1= {2}, num1={3}".format(t_size2, t_num2, size1, num1))
                    return False
            elif t_size2 == size2:
                if t_num2 != num2:
                    print("Error occurrences of groups differ here: tsize2={0}, tnum2= {1}, size2= {2}, num2={3}".format(t_size2, t_num2, size2, num2))
                    return False
            else:
                print("Error occurrences of groups differ here- This error case should not happen")
                return False
    #print("m1,2={0:>2d},{1:<2d}".format(t_num2, t_num1),end="")
    latex_comparison.write("{0:d},{1:d}&".format(t_num2, t_num1))
    return True


if __name__ == '__main__':
    main()


"""
[
  {
    "model":"groupings.allocation",
    "pk":1,
    "fields":{
      "num_participants":
      "num_rounds":
      "matching":
    }
  },
"""

# To use this script:
# Execute script
# Execute command "python manage.py loaddata matchings.json" from cmd in this directory

import sqlite3
from os import listdir
from os.path import isfile, join
import json
import collections

def main():
    mypath = "./allocations_data"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    result = []
    pkindex = 0

    for filename in onlyfiles:
        print("Loading data from: "+filename)
        pkindex = pkindex+1
        file = open(mypath+"/"+filename, 'r')
        text = "".join(file.readlines()).replace("\n","")
        matching = json.loads(text)
        num_rounds = len(matching)
        #print(num_rounds)
        expected_participants = filename.split("_")[1]
        expected_group_sizes = filename.split("(")[1].split(")")[0].split(",")
        #print(num_participants)
        if not is_correct(matching, expected_participants, expected_group_sizes):
            print("Error for matching in {0}".format(filename))
            #break
        num_participants=0
        for group in matching[0]:
            for participant in group:
                num_participants +=1
        result.append({
        "model":"groupings.allocation",
        "pk":pkindex,
        "fields":{
          "num_participants":num_participants,
          "num_rounds":num_rounds,
          "matching":str(matching)
        }})
        file.close()

    # ADD CORRECTNESS CHECK

    file = open("matchings.json", "w")
    json.dump(result, file)
    file.close()
    print ("done")


def is_correct(matching, expected_participants, expected_group_sizes):
    num_participants=0
    for group in matching[0]:
        for participant in group:
            num_participants +=1
    if str(num_participants) != expected_participants:
        print("participants are {0} instead of {1}".format(num_participants, expected_participants))
        return False
    for participant in range(num_participants):
        matched_with = []
        # checks whether participant appears exactly once each round
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
        print("Group sizes vary too much: {0}".format(group_sizes))
        return False
    for size in group_sizes:
        if size not in expected_group_sizes:
            print("Group sizes are not as advertises: {0} instead of {1}".format(group_sizes, expected_group_sizes))
            return False
    for size in expected_group_sizes:
        if size not in group_sizes:
            print("Group sizes are not as advertises: {0} instead of {1}".format(group_sizes, expected_group_sizes))
            return False
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

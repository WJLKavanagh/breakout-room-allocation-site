from django.db import models

# Create your models here.
class Allocation(models.Model):

    def __str__(self):
        
        a = eval(self.matching)     # evaluate allocation string
        # Here we will assume that the matching has at most 2 group sizes
        # This should already be checked by the populate script
        size1, num1 = 0, 0
        size2, num2 = 0, 0

        #for roundd in a:
        roundd = a[0]
        for group in roundd:
            if len(group) != size1 and size1 == 0:
                size1 = len(group)
                num1 += 1
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
        if size2 == 0:
            if num1 != 1:
                return "{1} participants for {0} rounds with {2} groups of size {3}".format(self.num_rounds, self.num_participants, num1, size1) #{0} rounds for {1} with group size of {2}
            else:
                return "{1} participants for {0} rounds with {2} group of size {3}".format(self.num_rounds, self.num_participants, num1, size1) #{0} rounds for {1} with group size of {2}
        if num1 == 1 and num2 == 1:
            return "{1} participants for {0} rounds with {2} group of size {3} and {4} group of size {5}".format(self.num_rounds, self.num_participants, num1, size1, num2, size2) #{0} rounds for {1} with group size between {2} and {3}
        elif num1 == 1 and num2 != 1:
            return "{1} participants for {0} rounds with {2} group of size {3} and {4} groups of size {5}".format(self.num_rounds, self.num_participants, num1, size1, num2, size2) #{0} rounds for {1} with group size between {2} and {3}
        elif num1 != 1 and num2 ==1:
            return "{1} participants for {0} rounds with {2} groups of size {3} and {4} group of size {5}".format(self.num_rounds, self.num_participants, num1, size1, num2, size2) #{0} rounds for {1} with group size between {2} and {3}
        return "{1} participants for {0} rounds with {2} groups of size {3} and {4} groups of size {5}".format(self.num_rounds, self.num_participants, num1, size1, num2, size2) #{0} rounds for {1} with group size between {2} and {3}

        # This is some legacy code that I have no idea what it is doing
        return str(eval(self.matching))     # evaluate allocation string
        ret_string = ""
        for round in a:
            ret_string = ret_string + str(round) + "\n\n"
        return ret_string

    num_participants = models.IntegerField("Total number of participants", default=1)
    num_rounds = models.IntegerField("Rounds of allocation", default=1)
    matching = models.CharField("Possible allocation", max_length=4000)

    def is_sound(self):

        """
        Returns True if every participant is matched with every other no more than once
        NAIVE.
        """

        a = eval(self.matching)     # evaluate allocation string
        participants = []
        for group in a[0]:
            # for every group in the first round:
            for participant in group:
                participants += [participant]
        for p in participants:
            # for every participant
            grouped_with = []   # list of those they've been with before
            for round in a:     # for every round of the allocation
                for g in round: # for every group in the round
                    if p in g:  # if the participant is in the group
                        for q in g:     # for every participant in the group
                            if q != p and q not in grouped_with:
                                # if they're new, add them to the list that P has been with
                                grouped_with += [q]
                            elif q != p and q in grouped_with:
                                # if they're old and not p, then the test has failed.
                                print("Failed. {0} is in a group with {1} more than once".format(p, q))
                                print(a)
                                return False
        return True

    def group_size(self):
        a = eval(self.matching)     # evaluate allocation string
        max_size = 0
        min_size = self.num_participants
        for round in a:
            for g in round:
                if len(g) > max_size:
                    max_size = len(g)
                if len(g) < min_size:
                    min_size = len(g)
        if min_size == max_size:
            return min_size
        return min_size, max_size

    @property
    def nice_display(self):
        """
        Formatting used for query accordion display
        """
        a = eval(self.matching)
        ret_string = ""
        for i in range(len(a)):
            ret_string += "Round " + str(i+1) + ":<br>&nbsp;&nbsp;&nbsp;&nbsp;"
            for j in range(len(a[i])):
                ret_string = ret_string + str(a[i][j])
                if j < len(a[i])-1:
                    ret_string += ", "
                else:
                    ret_string += "<br>"

        return ret_string

    @property
    def download_format(self):
        """
        Formatting equivalent to when emails are parsed.
        """
        a = eval(self.matching)
        ret_string = "["
        for r_i in range(len(a)):       # for round index 
            ret_string += "\n\t["     # round start
            for g_i in range(len(a[r_i])):      # for group index in round
                ret_string += "\n\t\t" + str(a[r_i][g_i])
                if g_i < len(a[r_i]) - 1:
                    ret_string += ","
                else:
                    ret_string += "\n\t]"
            if r_i < len(a) - 1:
                ret_string += ",\n"
            else:
                ret_string += "\n]"

        return ret_string


class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')

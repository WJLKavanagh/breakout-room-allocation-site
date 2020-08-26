from django.db import models

# Create your models here.
class Allocation(models.Model):

    def __str__(self):
        return "{0} participants in {1} rounds".format(self.num_participants, self.num_rounds)

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


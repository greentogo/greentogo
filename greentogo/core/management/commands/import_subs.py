import csv
import os.path

from django.core.management.base import BaseCommand

from core.models import Plan, UnclaimedSubscription


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs=1)

    def handle(self, *args, **options):
        filename = options['filename'][0]

        if not os.path.isfile(filename):
            print("{} is not a file!".format(filename))
            exit(1)

        # get plans for 1-4 boxes
        plans = Plan.objects.available()
        plandict = {}
        for x in range(1, 5):
            plandict[x] = plans.filter(number_of_boxes=x).first()

        num_created = 0
        num_found = 0

        def makeint(x):
            if not x:
                return 0
            return int(x)

        def getplan(cells):
            if cells[0]:
                return plandict[1]
            elif cells[1]:
                return plandict[2]
            elif cells[2]:
                return plandict[3]
            elif cells[3]:
                return plandict[4]

        with open(filename) as fh:
            reader = csv.reader(fh)
            next(reader)  # skip header line
            for row in reader:
                plan = None
                email = row[0]
                plancells = [makeint(x) for x in row[1:5]]
                if sum(plancells) != 1:
                    raise Exception("More than one plan for {}".format(email))
                plan = getplan(plancells)
                unsub, created = UnclaimedSubscription.objects.get_or_create(email=email, plan=plan)
                print("{} - {}".format(email, plan))
                if created:
                    num_created += 1
                else:
                    num_found += 1

        print("{} created, {} already existing".format(num_created, num_found))

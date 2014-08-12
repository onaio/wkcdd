import csv
import transaction

from sqlalchemy.orm.exc import NoResultFound

from wkcdd.models import (
    County,
    SubCounty,
    Constituency,
    Community,
    Location)


def update_locations_with_mis_codes():
    locations_list = []
    with open('data/mis_admin_boundaries.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        # Ignore first row
        reader.next()
        for row in reader:
            locations_list.append(row)

    county_map = {l[0]: l[1].strip(' County') for l in locations_list if l[0]}
    sub_county_map = {l[2]: l[3] for l in locations_list if l[0]}
    constituency_map = {l[4]: l[5] for l in locations_list if l[0]}
    community_list = [(l[6], l[7], l[5])
                      for l in locations_list if l[0]]
    with transaction.manager:
        update_location_domains(County, county_map)
        update_location_domains(SubCounty, sub_county_map)
        update_location_domains(Constituency, constituency_map)
        update_community_locations(community_list)
        update_locations_without_mis_codes()


def update_location_domains(klass, location_codes):
    for code, location_name in location_codes.iteritems():
        try:
            location = klass.get(klass.name == location_name,
                                 klass.mis_code.is_(None))
            location.mis_code = code
            location.save()
        except NoResultFound:
            print "[info] {} location not found".format(location_name)
            pass


def update_community_locations(location_list):
    for code, community_name, constituency_name in location_list:
        try:
            constituency = Constituency.get(
                Constituency.name == constituency_name)
            location = Community.get(Community.name == community_name,
                                     Community.parent == constituency)
            location.mis_code = code
            location.save()
        except NoResultFound:
            print "[info] {} location not found".format(community_name)
            pass


def update_locations_without_mis_codes():
    locations_list = []
    with open('data/additional_location_mis.csv', 'rbU') as csvfile:
        reader = csv.reader(csvfile)
        # Ignore first row
        reader.next()
        for row in reader:
            locations_list.append(row)

    for name, code in locations_list:
        try:
            location = Location.get(Location.name == name,
                                    Location.mis_code.is_(None))
            location.mis_code = code
            location.save()
        except NoResultFound:
            print "[info] {} location not found".format(name)
            pass

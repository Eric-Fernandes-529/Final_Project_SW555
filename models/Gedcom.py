from models.Individual import Individual
from models.Family import Family

class Gedcom:

    def __init__(self, path, supportTags):
        self._supportTags = supportTags
        self._individuals = {}
        self._families = {}
        self._data = self.readfile(path)

    def readfile(self, path):
        """
        res[3] returns a dictionary with index as the starting index of either an individual or a family.
        Each attribute of that object will have a corresponding line number
        { index: {attribute field: line number in GEDCOM}
        """
        res = [[], [], [], {}]  # [[level, tag, arguments], [start indices of indi], [start indices of fam], {index:{attribute: line number}]
        f = open(path, "r")
        index = 0
        lineNumber = 0

        for line in f:
            level, tag, arguments = self.parseline(line)
            if tag not in self._supportTags:  # skip unsupported tags
                lineNumber += 1
                continue
            res[0].append([level, tag, arguments])
            #appending index and linenumbers for individual
            if tag == "INDI":
                res[1].append(index)
                res[3][index] = {}
                res[3][index]["INDI ID"] = lineNumber
                x = index
            elif tag == "NAME" and level == '1':
                res[3][x]["NAME"] = lineNumber
            elif tag == "SEX":
                res[3][x]["SEX"] = lineNumber
            elif tag == "BIRT":
                res[3][x]["BIRT"] =  lineNumber + 1
            elif tag == "DEAT":
                res[3][x]["DEAT"] = lineNumber + 1
            elif tag == "FAMC":
                if "FAMC" in res[3][x]:
                    res[3][x]["FAMC"].append(lineNumber)
                else:
                    res[3][x]["FAMC"] =[]
                    res[3][x]["FAMC"].append(lineNumber)
            elif tag == "FAMS":
                if "FAMS" in res[3][x]:
                    res[3][x]["FAMS"].append(lineNumber)
                else:
                    res[3][x]["FAMS"] = []
                    res[3][x]["FAMS"].append(lineNumber)
            #appending index and line numbers for FAM
            elif tag == "FAM":
                if not res[2]:
                    res[1].append(index)  # the first start index for family is the last end index for indis
                res[2].append(index)
                res[3][index] = {}
                res[3][index]["FAM ID"] = lineNumber
                y = index
            elif tag == "HUSB":
                res[3][y]["HUSB"] = lineNumber
            elif tag == "WIFE":
                res[3][y]["WIFE"] = lineNumber
            elif tag == "CHIL":
                if "CHIL" in res[3][y]:
                    res[3][y]["CHIL"].append(lineNumber)
                else:
                    res[3][y]["CHIL"] = []
                    res[3][y]["CHIL"].append(lineNumber)
            elif tag == "MARR":
                res[3][y]["MARR"] = lineNumber + 1
            elif tag == "DIV":
                res[3][y]["DIV"] = lineNumber + 1

            index += 1
            lineNumber += 1

        res[2].append(index)  # end index for fam
        f.close()
        return res

    def parseline(self, line):
        line = line.split()
        level, tag, arguments = line[0], line[1], line[2:]
        if arguments and arguments[0] in ["INDI", "FAM"]:
            tag, arguments = arguments[0], tag
        return level, tag, arguments

    def peek(self):
        for line in self._data[0]:
            level, tag, arguments = line[0], line[1], line[2:]
            print("    " * int(level), level, tag, arguments)

    def get_data(self):
        return self._data

    def get_individuals(self):
        return self._individuals

    def get_families(self):
        return self._families

    def parse(self):
        from models.Individual import Individual
        from models.Family import Family
        offset = 0
        for i in range(len(self._data[1]) - 1):  # enumerate individuals
            start_index = self._data[1][i]
            end_index = self._data[1][i + 1]
            # print(self._data[0][start_index:end_index])
            # TODO: check deplicated ids
            id = self._data[0][start_index][2]
            if id in self._individuals:
                offset += 1
                id = "@I" + str(int(id[2:-1]) + offset) + "@"
            new_indi = Individual(id)
            new_indi.set_lineNum(self._data[3][start_index])
            self._individuals[id] = new_indi
            # print(start_index, end_index)
            for j in range(start_index + 1, end_index):
                level, tag, arguments = self._data[0][j]
                if tag == "NAME":
                    new_indi.set_name("".join(arguments))
                elif tag == "SEX":
                    new_indi.set_gender(arguments[0])
                elif tag == "BIRT":  # set missing dates to Jan/01
                    j += 1
                    level, tag, arguments = self._data[0][j]
                    try:
                        new_indi.set_birthDate(arguments)
                    except ValueError as e:
                        print(e)  # TODO:how to handle error?
                elif tag == "DEAT":
                    j += 1
                    level, tag, arguments = self._data[0][j]
                    new_indi.set_deathDate(arguments)
                elif tag == "FAMS":
                    if arguments[0] not in self._families:
                        new_fam = Family(arguments[0])
                        self._families[arguments[0]] = new_fam
                    new_indi.add_to_family(self._families[arguments[0]])
                elif tag == "FAMC":
                    if arguments[0] not in self._families:
                        new_fam = Family(arguments[0])
                        self._families[arguments[0]] = new_fam
                    new_indi.set_parentFamily(self._families[arguments[0]])
        offset = 0
        for i in range(len(self._data[2]) - 1):
            start_index = self._data[2][i]
            end_index = self._data[2][i + 1]
            # print(self._data[0][start_index:end_index])
            id = self._data[0][start_index][2]
            # if id in self._families:  #TODO: handle duplicate
            #     offset+=1
            #     id = "@F" + str(int(id[2:-1]) + offset) + "@"
            new_fam = Family(id)
            new_fam.set_lineNum(self._data[3][start_index])
            self._families[id] = new_fam
            for j in range(start_index + 1, end_index):
                level, tag, arguments = self._data[0][j]
                # print(level, tag, arguments)
                if tag == "HUSB":
                    new_fam.set_husband(self._individuals[arguments[0]])
                elif tag == "WIFE":
                    new_fam.set_wife(self._individuals[arguments[0]])
                elif tag == "CHIL":
                    new_fam.add_child(self._individuals[arguments[0]])
                elif tag == "MARR":
                    j += 1
                    level, tag, arguments = self._data[0][j]
                    # print(level, tag, arguments)
                    try:
                        new_fam.set_marriedDate(arguments)
                    except:
                        continue
                elif tag == "DIV":
                    j += 1
                    level, tag, arguments = self._data[0][j]
                    # print(level, tag, arguments)
                    try:
                        new_fam.set_divorcedDate(arguments)
                    except:
                        continue

    '''
    Move this function from individual.py to gedcom.py
    '''

    def dates_before_current_date(self):
        from datetime import date
        today = date.today()
        for _, indi in self._individuals:
            if not indi.get_birthDate(): raise AttributeError("Error: missing birthdate for individual")
            if not (today - date(indi.get_birthDate())).days < 0: return False
            if not indi.get_deathDate() == None:
                if not (today - date(indi.get_deathDate())).days < 0: return False

        for _, fam in self._families:
            if not fam.get_marriedDate(): raise AttributeError("Error: missing marriedDate for family")
            if not (today - date(fam.get_marriedDate())).days < 0: return False
            if not fam.get_divorcedDate() == None:
                if not (today - date(fam.get_divorcedDate())).days < 0: return False

        return True

    def Unique_IDs(self):
        pass

    # Finshed in mainfunction.

    def unique_name_and_birth_date(self):
        dic = set()
        for indi in self._individuals.values():
            if indi.get_birthDate():
                key = indi.get_name().replace("/", "") + "a".join(list(map(str, indi.get_birthDate())))
                # print(key)
                if key not in dic:
                    dic.add(indi)
                else:
                    return False
        return True

    def unique_families_by_spouses(self):
        """user story 24 No more than one family with the same spouses by name and the same marriage date should appear in a GEDCOM file """
        check_list = []
        for _, family in self._families:
            if not family.get_husband() or not family.get_wife(): raise AttributeError("no husband or wife")
            if not family.get_husband().get_name() or not family.get_wife().get_name(): raise AttributeError(
                "no husband or wife name")
            if not family.get_marriedDate(): raise AttributeError("no marriage date")
            this_fam_info = [family.get_husband().get_name(), family.get_wife.get_name(), family.get_marriedDate()]
            if check in check_list: return False
            check_list.append(this_fam_info)

        return True

    def unique_first_names_in_families(self):
        """user story 25 No more than one child with the same name and birth date should appear in a family"""

        for _, family in self._families:
            check_list = []
            for child in family.get_children():
                if not child.get_name() or not child.get_birthDate(): raise AttributeError(
                    "no name or birthdate for child")
                child_info = [child.get_name(), child.get_birthDate()]
                if child_info in check_list: return False
                check_list.append(child_info)

        return True

    def include_individual_ages(self):
        pass

    def corresponding_entries(self):
        """ user story 26 the information in the individual and family records should be consistent."""
        for key_id, indi in self._individuals:
            if indi.get_parentFamily():
                flag = False
                for child in indi.get_parentFamily().get_children():
                    if child.get_id() == key_id: flag = True
                if not flag: return False

            for fam in indi.get_family():
                if not fam.get_husband() and not fam.get_wife(): return False
                if not (fam.get_husband().get_id() == key_id or fam.get_wife().get_id() == key_id): return False

        for key_id, fam in self._families:
            if fam.get_husband():
                flag = False
                for check_fam in fam.get_husband().get_family():
                    if check_fam.get_id() == key_id: flag = True
                if not flag: return False

            if fam.get_wife():
                flag = False
                for check_fam in fam.get_wife().get_family():
                    if check_fam.get_id == key_id: flag = True
                if not flag: return False

            for child in fam.get_children():
                if not child.get_parentFamily(): return False
                if child.get_parentFamily().get_id() == key_id: return False

        return True

    # def list_deceased(self):
    #     """us 29 list all deceased individuals in a gedcom file"""
    #     deceasedPeople=[]
    #     if self._individuals.get_deathDate()==None: raise AttributeError("no one deceased")
    #     for individual in self._individuals():
    #         if self.get_deathDate() != None:
    #             deceasedPeople.append(self.get_id())
    #     return deceasedPeople
    #
    #
    # def list_living_married(self):
    #     """list all living married people in a Gedcom file"""
    #     marriedPeople=[]
    #     if not self.get_wife or self.get_husband: raise AttributeError("no wife or husband found for spouse")
    #     for family in self._families():
    #         if self.get_husband==self.get_id and self.husband.get_deathDate == None:
    #             marriedPeople.append(self.get_husband)
    #         if self.get_wife==self.get_id and self.get_wife.get_deathDate==None:
    #             marriedPeople.append(self.get_wife)
    #     return marriedPeople

    # compares each families's marriage dates(month and day) to today's date, returns array of members with upcoming anniversaries
    # return empty array if no dates are found

    def list_upcoming_anniversaries(self):
        """
        return couples tuple of ids
        """

        from datetime import date, datetime
        indiUpcomingAnniversaries = []
        today = date.today()
        if(len(self._families) == 0):
            raise AttributeError("GEDCOM file doesn't have any families")
        for fam in self._families.values():
            if (today - date(*fam.get_marriedDate())).days % 365 <= 30: #to test
                if(fam.get_husband().get_deathDate() or fam.get_wife().get_deathDate()):
                    continue
                else:
                    indiUpcomingAnniversaries.append((fam.get_husband().get_id(),fam.get_wife().get_id()))

        return indiUpcomingAnniversaries

    def list_upcoming_birthdays(self):
        from datetime import date
        output_list = []
        today = date.today()
        for key in self._individuals:
            indi = self._individuals[key]
            if not indi.get_birthDate() or not indi.get_birthDate()[1] or not indi.get_birthDate()[2] or indi.get_deathDate(): continue

            day_diff = (today - indi.get_birthDate()).days % 365

            if 0 <= day_diff < 30: output_list.append(key)

        return output_list

    def list_resent_survivors(self):
        from datetime import date
        output = {}
        for key in self._individuals:
            indi = self._individuals[key]
            if not indi.get_deathDate(): continue

            death = date(*indi.get_deathDate())

            if(0 <= (date.today() - death).days < 30):

                info = [[],[]] #0: spouses, 1: descendants
                if not indi.get_gender(): continue
                for fam in indi.get_family():
                    if indi.get_gender() == "M":
                        if not indi.get_wife(): continue
                        info[0].append(indi.get_wife().get_id())
                    else:
                        if not indi.get_husband(): continue
                        info[0].append(indi.get_husband().get_id())

                    info[1] += indi.get_children()

                output[indi.get_id()] = tuple(info)

        return output

    def list_deceased(self):
        """us 29 list all deceased individuals in a gedcom file"""
        deceasedPeople=[]
        if self._individuals.get_deathDate()==None: raise AttributeError("no one deceased")
        for individual in self._individuals():
            if self.get_deathDate() != None:
                deceasedPeople.append(self.get_id())
        return deceasedPeople


    def list_living_married(self):
        """list all living married people in a Gedcom file"""
        marriedPeople=[]
        if not self.get_wife or self.get_husband: raise AttributeError("no wife or husband found for spouse")
        for family in self._families():
            if self.get_husband==self.get_id and self.husband.get_deathDate == None:
                marriedPeople.append(self.get_husband)
            if self.get_wife==self.get_id and self.get_wife.get_deathDate==None:
                marriedPeople.append(self.get_wife)
        return marriedPeople 
    
    def list_large_age_differences(self):
        "US34, List all couples who were married when the older spouse was more than twice as old as the younger spouse"

        res = []

        for id in self._families:
            family = self._families[id]
            if not family.get_husband() or not family.get_wife(): continue
            husband = family.get_husband()
            wife = family.get_wife()

            if not husband.get_birthDate() or not wife.get_birthDate(): continue

            husband_age = husband.get_age()
            wife_age = wife.get_age()
            age_difference = husband_age - wife_age
            if age_difference > 0 and age_difference > wife_age:
                res.append((husband.get_id(), wife.get_id()))
            if age_difference < 0 and -age_difference > husband_age:
                res.append((husband.get_id(), wife.get_id()))
        return res


    def list_recent_birth(self):
        "US35, List all people in a GEDCOM file who were born in the last 30 days"

        recent_birth = []

        for id in self._individuals:
           indi = self._individuals[id]
           if not indi.get_birthDate(): continue
           if 0<= indi.get_age(days = True) < 30: recent_birth.append(id)
        return recent_birth

    def list_recent_deaths(self):
        from datetime import date
        from datetime import timedelta
        deathPeople = []
        for indi in self._individuals.values():
            if indi.get_deathDate[0]>(date.today() - timedelta(30)).strftime("%Y"):
                deathPeople.append(indi.get_name)
            elif indi.get_deathDate[0]==(date.today() - timedelta(30)).strftime("%Y"):
                if indi.get_deathDate[1]>(date.today() - timedelta(30)).strftime("%m"):
                    deathPeople.append(indi.get_name)
                elif indi.get_deathDate[1]==(date.today() - timedelta(30)).strftime("%m"):
                    if indi.get_deathDate[2]>(date.today() - timedelta(30)).strftime("%d"):
                        deathPeople.append(indi.get_name)

        return deathPeople

    def list_multiple_births(self):
        dic = {}
        multiple_birth = []
        for indi in self._individuals.values():
            key = indi.get_parent_family().get_id()+str(indi.get_birthDate())
            if key in dic:
                dic[key].append(indi.get_id())
            else:
                dic[key] = [indi.get_id()]
        for list1 in dic.values():
            if len(list1)>1 :
                multiple_birth.append(list1)
        return multiple_birth
    
    def list_living_single(self):
        from models.Individual import Individual
        singlePeople=[]
        for ind in self.get_individuals():
            if not self.get_individuals()[ind].get_deathDate():
                if self.get_individuals()[ind].get_age()>30:
                    if len(self.get_individuals()[ind].get_family())==0:
                        singlePeople.append(self.get_individuals()[ind])
        return singlePeople
    
    def list_orphans(self):
        from models.Individual import Individual
        from models.Family import Family
        orphans=[]
        for ind in self.get_individuals():
            if self.get_individuals()[ind].get_age()<18:
                if self.get_individuals()[ind].get_parent_family():
                    if self.get_individuals()[ind].get_parent_family().get_husband() and self.get_individuals()[ind].get_parent_family().get_wife():
                        if self.get_individuals()[ind].get_parent_family().get_husband().get_deathDate() and self.get_individuals()[ind].get_parent_family().get_wife().get_deathDate():
                            orphans.append(self.get_individuals()[ind])
                    else: raise AttributeError("Missing wife or husband: "+self.get_individuals()[ind].get_parent_family().get_id())
                else: raise AttributeError("Missing parent family: "+self.get_individuals()[ind].get_id())
        return orphans
    def sort_individual(self):
        from models.Individual import Individual
        sorted=[]
        for ind in self.get_individuals():
            sorted.append(self.get_individuals()[ind].get_name())
        sorted.sort()
        return sorted
    "US 56 functions"
    def fix_child_to_family(self, individual, family):
        from models.Individual import Individual
        from models.Family import Family
        ind.set_parentFamily(individual)
    def fix_family_to_child(self, individual, family):
        from models.Individual import Individual
        from models.Family import Family
        family.add_child(individual)
    def fix_parent_to_family(self, individual, family):
        from models.Individual import Individual
        from models.Family import Family
        individual.add_to_family(family)
    def fix_family_to_parent(self, individual, family):
        from models.Individual import Individual
        from models.Family import Family
        if(individual.get_gender()=="F"):
            family.set_wife(individual)
        else:
            family.set_husband(individual)

if __name__ == "__main__":
    SUPPORT_TAGS = {"INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "FAM", "MARR", "HUSB", "WIFE", "CHIL",
                    "DIV", "DATE", "HEAD", "TRLR", "NOTE"}
    g1 = Gedcom("../testing_files/Jiashu_Wang.ged", SUPPORT_TAGS)#testing_files/Jiashu_Wang.ged
    # for i in range(len(g1.get_data()[0])):
    #     print(i,g1.get_data()[0][i])
    # for i in range(len(g1.get_data()[1])):
    #     print(g1.get_data()[1][i])
    # print(g1.get_data(),sep='/n')
    g1.parse()
    g1.peek()
    # print(g1.get_individuals(),g1.get_families())
    # print(len(g1.get_individuals()),g1.get_individuals()["@I2@"].get_birthDate())
    g1.unique_name_and_birth_date()
    # print("what")
    # offset = 11
    # id = "@I123@"
    # print("@I"+str(int(id[2:-1])+offset)+"@")
    #print(g1.get_families().values())
# if __name__ == "__main__":
#     SUPPORT_TAGS = {"INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "FAM", "MARR", "HUSB", "WIFE", "CHIL",
#                     "DIV", "DATE", "HEAD", "TRLR", "NOTE"}
#     g1 = Gedcom("../testing_files/test_date_validation.ged", SUPPORT_TAGS)  # testing_files/Jiashu_Wang.ged
#     g1.peek()
# g1.parse()
# print(g1.get_individuals().keys(), g1.get_families().keys())
# print(g1.get_individuals()["@I4@"].get_birthDate())


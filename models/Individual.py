class Individual:
    '''
    This is the class for individual.
    id is the only variable that is required. If other variable does not exist, it would return None
    If children/spouse does not exist, it would return an empty list

    all date value are passed in as str, and saved as tuple with formate (year, month, day)
    '''

    def __init__(self, id: str):
        self.id = id
        self._name = None
        self._firstName = None
        self.lastName = None
        self._gender = None
        self._birthDate = None
        self._deathDate = None
        #change made here
        self._family = []
        self._parentFamily = None

    def get_id(self) -> str:
        return self.id

    def get_name(self) -> str:
        return self._name

    def get_gender(self) -> str:
        return self._gender

    def get_birthDate(self) -> tuple:
        return self._birthDate

    def get_age(self, days=False) -> int:
        """
        :param days: a flag indicates whether you want the years or the days
        :return: Return age in base of years or days. Would return -1 if no birthday info

        """
        import datetime
        if not self._birthDate: return -1
        today = datetime.date.today()
        lived_days = (today - datetime.date(*self._birthDate)).days
        return lived_days // 365 if not days else lived_days

    def get_deathDate(self) -> tuple:
        return self._deathDate

    def get_family(self) ->[]:
        return self._family

    def get_parent_family(self):
        return self._parentFamily

    def set_name(self, name: list) -> None:
        # if not isinstance(name, str): raise TypeError("input has to be a str type")
        self._name = name
        self._firstName = name[0]
        self._lastName = name[1]

    def set_gender(self, gender: str) -> None:
        # if not isinstance(gender, str): raise TypeError("input has to be a str type")
        self._gender = gender

    def set_birthDate(self, birth_date: list) -> None:
        # if not isinstance(birth_date, str): raise TypeError("input has to be a str type")
        if all(isinstance(v, int) for v in birth_date):
            self._birthDate = birth_date
            return
        self._birthDate = self.change_date_formate(birth_date)

    def set_deathDate(self, death_date: list) -> None:
        # if not isinstance(death_date, str): raise TypeError("input has to be a str type")
        self._deathDate = self.change_date_formate(death_date)

    def add_to_family(self, familylist) -> None:
        # makes sure child can not set his/her family as his/her parent family
        # if family.get_children():
        #     for child in family.get_children():
        #         if child == self:
        #             raise ValueError("Can not set parent family as one's family")
        self._family.append(familylist)

    def set_parentFamily(self, parent_family) -> None:
        # if not isinstance(parent_family, family): raise TypeError("input has to be a family type")
        self._parentFamily = parent_family

    def change_date_formate(self, date: list) -> tuple:
        '''
        Would take the string input and convert it into a int tuple:(year, month, day)
        '''

        monthList = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8, "SEP": 9,
                     "OCT": 10, "NOV": 11, "DEC": 12}
        return int(date[2]), monthList[date[1]], int(date[0])

    def dates_before_current_date(self):
        pass

    def birth_before_marriage(self):
        import datetime
        if not self._birthDate or not self._parentFamily or not self._parentFamily.get_marriedDate():
            return True
        birthday = datetime.datetime(*self._birthDate)
        marriageDate = datetime.datetime(*self._parentFamily.get_marriedDate())
        return birthday < marriageDate

    def birth_before_death(self):
        import datetime
        if not self._birthDate or not self._deathDate:
            return True
        if not isinstance(self._birthDate, tuple) or not isinstance(self._deathDate, tuple):
            raise ValueError("birthday or deathDate not in tuple format!")

        birthday = datetime.datetime(*self._birthDate)
        deathDate = datetime.datetime(*self._deathDate)
        return birthday < deathDate

    def less_then_150_years_old(self):
        if self.get_age() > 150:
            raise ValueError("People" + self.get_id() + "is too old")
        return self.get_age() < 150

    def no_bigamy(self) -> bool:
        if (len(self._family) <= 1): return True
        marrageAgeList = []
        birthDate = self._birthDate
        if not self._family:
            return True
        for each_marrage in self._family:
            if not each_marrage.get_marriedDate(): continue
            marrageAge = each_marrage.get_marriedDate()[0] - birthDate[0] + (
                    each_marrage.get_marriedDate()[1] - birthDate[1]) / 12 + (
                                 each_marrage.get_marriedDate()[2] - birthDate[2]) / 365
            devorceAge = None
            if (each_marrage.get_divorcedDate() is not None): devorceAge = each_marrage.get_divorcedDate()[0] - \
                                                                           birthDate[
                                                                               0] + (each_marrage.get_divorcedDate()[
                                                                                         1] - birthDate[1]) / 12 + (
                                                                                   each_marrage.get_divorcedDate()[
                                                                                       2] -
                                                                                   birthDate[2]) / 365
            for Age_range in marrageAgeList:
                if (Age_range[1] == devorceAge and devorceAge == None):
                    return False
                elif ((not Age_range[1] == devorceAge) and devorceAge == None):
                    if (not (Age_range[0] < marrageAge and Age_range[1] < marrageAge)):
                        return False
                elif ((not Age_range[1] == devorceAge) and Age_range[1] == None):
                    if (not (marrageAge < Age_range[0] and devorceAge < Age_range[0])): return False
                else:
                    if (marrageAge > Age_range[0] and marrageAge < Age_range[1]):
                        return False
                    elif (devorceAge > Age_range[0] and devorceAge < Age_range[1]):
                        return False

            marrageAgeList.append((marrageAge, devorceAge))
        return True

    def parents_not_too_old(self):
        pass

    def aunts_and_uncles(self):
        pass

    def first_cousins_should_not_marry(self):
        pass  # did not understand the question, move to the place you like

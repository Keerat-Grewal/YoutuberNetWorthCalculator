from hash_quad import *
import string


class Concordance:

    def __init__(self):
        self.stop_table = None          # hash table for stop words
        self.concordance_table = None   # hash table for concordance

    def load_stop_table(self, filename):
        """ Read stop words from input file (filename) and insert each word as a key into the stop words hash table.
        Starting size of hash table should be 191: self.stop_table = HashTable(191)
        If file does not exist, raise FileNotFoundError"""
        self.stop_table = HashTable(191)

        try:
            file = open(filename, "r")
        except FileNotFoundError:
            raise FileNotFoundError

        read_all_lines = False

        while not read_all_lines:
            line = file.readline()
            if line == "":
                read_all_lines = True
            if not read_all_lines:
                stop_word = line.strip()
                self.stop_table.insert(stop_word)

        file.close()

    def load_concordance_table(self, filename):
        """ Read words from input text file (filename) and insert them into the concordance hash table,
        after processing for punctuation, numbers and filtering out words that are in the stop words hash table.
        Do not include duplicate line numbers (word appearing on same line more than once, just one entry for that line)
        Starting size of hash table should be 191: self.concordance_table = HashTable(191)
        If file does not exist, raise FileNotFoundError"""
        self.concordance_table = HashTable(191)
        try:
            file = open(filename, "r")
        except FileNotFoundError:
            raise FileNotFoundError

        read_all_lines = False
        line_number = 0
        while not read_all_lines:
            line = file.readline().lower()
            if line == "":
                read_all_lines = True
            line_number += 1
            if not read_all_lines:
                new_line = self.punctuation_removal(line)
                for i in new_line:
                    if not(self.stop_table.in_table(i)) and not(self.is_int_or_float(i)):
                        index = self.concordance_table.get_index(i)
                        if index is not None:
                            value = self.concordance_table.hash_table[index][1]
                            length_of_value = len(value)
                            if value[length_of_value - 1] != line_number:
                                value.append(line_number)
                                new_value = (self.concordance_table.hash_table[index][0], value)
                                self.concordance_table.hash_table[index] = new_value
                        else:
                            self.concordance_table.insert(i, [line_number])

        file.close()

    def write_concordance(self, filename):
        """ Write the concordance entries to the output file(filename)
        See sample output files for format."""
        file = open(filename, "w")
        keys = self.concordance_table.get_all_keys()
        keys.sort()
        for i in range(len(keys)):
            index = self.concordance_table.get_index(keys[i])
            key = self.concordance_table.hash_table[index][0]
            values = self.concordance_table.hash_table[index][1]
            string_of_values = ""
            for j in values:
                string_of_values += " " + str(j)

            content = "{0}:{1}".format(key, string_of_values)

            if i == len(keys) - 1:
                file.write(content)
            else:
                file.write(content + "\n")

        file.close()

    def punctuation_removal(self, line):
        """This functions takes in a line and creates a new line without any punctuation in it. It makes sure to
        view dashes as spaces."""
        punctuation = string.punctuation

        res = ""

        for i in line:
            if i == "-":
                res += " "
            elif i in punctuation:
                res += ""
            else:
                res += i

        return res.split()

    def is_int_or_float(self, word):
        """This function checks if the given string is a number (float or integer) and returns True if it
        is a number and False if it is not a number."""
        try:
            integer = float(word)
            return True
        except ValueError:
            return False

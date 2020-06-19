

class HashTable:

    def __init__(self, table_size):         # can add additional attributes
        self.table_size = table_size        # initial table size
        self.hash_table = [None] * table_size  # hash table
        self.num_items = 0                  # empty hash table

    def insert(self, key, value=None):

        index = self.horner_hash(key)
        entry = (key, value)

        i = 0
        new_indx = index
        while self.hash_table[new_indx] is not None and self.hash_table[new_indx][0] != key:
            i += 1
            new_indx = (index + (i ** 2)) % self.table_size
        place = new_indx
        if self.hash_table[place] is None:
            self.num_items += 1
        self.hash_table[place] = entry

        # check load factor, rehash if greater than 0.5
        if self.get_load_factor() > 0.5:
            old_table = self.hash_table
            self.table_size = (self.table_size * 2) + 1
            self.hash_table = [None] * self.table_size
            for i in range(len(old_table)):
                if old_table[i] is not None:
                    new_index = self.horner_hash(old_table[i][0])
                    new_entry = old_table[i]
                    i = 0
                    while self.hash_table[(new_index + (i ** 2)) % self.table_size] is not None:
                        i += 1
                    place = (new_index + (i ** 2)) % self.table_size
                    self.hash_table[place] = new_entry

    def horner_hash(self, key):
        ''' Compute and return an integer from 0 to the (size of the hash table) - 1
        Compute the hash value by using Horner’s rule, as described in project specification.'''
        total = 0
        for i in range(min(len(key), 8)):
            total += ord(key[i]) * (31 ** (len(key) - 1 - i))
        return total % self.table_size

    def in_table(self, key):
        ''' Returns True if key is in an entry of the hash table, False otherwise.'''
        index = self.get_index(key)
        if index is None:
            return False
        return True

    def get_index(self, key):
        ''' Returns the index of the hash table entry containing the provided key.
        If there is not an entry with the provided key, returns None.'''
        index = self.horner_hash(key)

        i = 0
        while self.hash_table[(index + (i ** 2)) % self.table_size] is not None and \
                self.hash_table[(index + (i ** 2)) % self.table_size][0] != key:
            i += 1
        place = (index + (i ** 2)) % self.table_size
        if self.hash_table[place] is not None and self.hash_table[place][0] == key:
            return place
        else:
            return None

    def get_all_keys(self):
        ''' Returns a Python list of all keys in the hash table.'''
        list_of_keys = []
        for i in range(len(self.hash_table)):
            if self.hash_table[i] is not None:
                list_of_keys.append(self.hash_table[i][0])
        return list_of_keys

    def get_value(self, key):
        ''' Returns the value associated with the key.
        If key is not in hash table, returns None.'''
        index = self.get_index(key)
        if index is None:
            return None
        return self.hash_table[index][1]

    def get_num_items(self):
        ''' Returns the number of entries in the table.'''
        return self.num_items

    def get_table_size(self):
        ''' Returns the size of the hash table.'''
        return self.table_size

    def get_load_factor(self):
        ''' Returns the load factor of the hash table (entries / table_size).'''
        return self.num_items / self.table_size


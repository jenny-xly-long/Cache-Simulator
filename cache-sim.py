from collections import defaultdict, OrderedDict
import random
import math
import argparse
from typing import OrderedDict
from mxm import mxm
from mxm_blocked import mxm_blocked
from daxpy import daxpy
'''
Word (double) is 8 bytes for this simulation
'''
WORD_SIZE = 8

class CPU:
    """ The CPU class contains 4 instruction methods to load, store doubles and to add, multiply doubles

    Attributes
    ----------
    cache_size : int
        Custom input of cache size, default 65536 bytes.
    ram_size : int
        Ram size designed as the minimum memory needed to hold the data structure of a given algorithm.
    block_size : int
        Custom input of block size, default 64 bytes.
    ram_size : int
        Ram size designed as the minimum memory needed to hold the data structure of a given algorithm.
    num_in_set : int
        Custom n-way associativity, default 2.
    cache_sets : int
        Number of sets in the cache.
    r : str
        Replacement policy, default 'LRU'.
    d : int
        Matrix/vector dimension used in a given algorithm.
    a : str
        Specified algorithm, default 'mxm_block'.
    f : int
        Blocking factor in tiled matrix multiplication, default 32.
    _cache : OrderedDict
        Cache is implemented with an OrderedDict of OrderedDict of dict.
        The first layer OrderedDict has indices as key and OrderedDict as value.
        The second layer of OderedDict has ram block number as key and dict as value.
        The inner dict has address as key and the stored double as value. 
    _ram : defaultdict
        Ram is implemented with a defaultdict of dict.
        The outer defaultdict has ram block number as key and dict as value.
        The inner dict has address as key and the stored double as value.
    instruction_count : str
        Cumulated count of instructions for a given algorithm.
    r_hit : int
        Cumulated count of cache read hit for a given algorithm.
    r_miss : str
        Cumulated count of cache read miss for a given algorithm.
    w_hit : int
        Cumulated count of cache write hit for a given algorithm.
    w_miss : int
        Cumulated count of cache write miss for a given algorithm.

    """
    def __init__(self,c, b, n, r, a, d, f, ram_size):
        """Initiate the CPU with its features

        Parameters
        ----------
        c : int
            Cache size.
        b : int
            Block size.
        n : int
            Associativity.
        r : str
            Replacement method.
        a : str
            Algorithm.
        d : int
            Matrix/vector dimension.
        f : int
            Blocking factor in tiled matrix multiplication.
        ram_size : int
            Ram size needed for the given algorithm data structure.

        """
        self.cache_size = c
        self.ram_size = ram_size
        self.block_size = b
        self.num_in_set = n
        self.cache_sets = c // b // n
        self.r = r
        self.d = d
        self.a = a
        self.f = f
        cache = OrderedDict()
        for i in range(self.cache_sets):
            cache[i] = OrderedDict()
        ram = defaultdict(dict)
        self._cache = cache
        self._ram = ram
        
        self.instruction_count = 0
        self.r_hit = 0
        self.r_miss = 0
        self.w_hit = 0
        self.w_miss = 0

    def parseAddress(self, address):
        """Parse a given address into tag, index and offset.

        Parameters
        ----------
        address
            The address in memory.
        
        Returns
        -------
        (int, int, int)
            A tuple containing tag, index, offset.
        """
        offsetBit = int(math.log2(self.block_size))
        indexBit = int(math.log2(self.cache_sets))
        tagBit = 64 - offsetBit - indexBit

        offset = (address) & ((1 << offsetBit) - 1)
        index = (address >> offsetBit) & ((1 << indexBit) - 1)
        tag = (address >> (offsetBit + indexBit)) & ((1 << tagBit) - 1)
  
        return offset, index, tag
    
    def loadDouble(self, address):
        """Load a double from memory.

        Parameters
        ----------
        address
            The address in memory.
        
        Returns
        -------
        double
            The double stored at the given memory address.
        """
        self.instruction_count += 1
        offset, index, tag = self.parseAddress(address)
        # The ram_index indicates which addresses fall into the same block, which later help us to load the entire block into cache
        ram_index = address // self.block_size 

        if ram_index in self._cache[index]:
            self.r_hit += 1
            # An OrderedDict keeps the most recently inserted element at the end. By removing the cache hit block and then immediately add it back to the OrderedDict,
            # the cache hit block will remain the the end of the OrderedDict to indicate it is the most recently used.
            if self.r == 'LRU':
                item = self._cache[index].pop(ram_index)
                self._cache[index][ram_index] = item 
        else:
            self.r_miss += 1
            if len(self._cache[index]) < self.num_in_set:
                # add the entire block that contain this address
                self._cache[index][ram_index] = self._ram[ram_index] 
            else:
                if self.r == 'random':
                    # pick a random key-value pair to evict
                    ram_index_list = list(self._cache[index].keys())
                    rand = random.choice(ram_index_list)
                    del self._cache[index][rand]
                else:
                    # for FIFO and LRU, evict the first element
                    self._cache[index].popitem(last = False)
                # Add the new block to cache
                self._cache[index][ram_index] = self._ram[ram_index] 

        return self._cache[index][ram_index][address] #self._ram[ram_index][address] 
    
    def storeDouble(self, address, value):
        """Load a double from memory.

        Parameters
        ----------
        address
            The address in memory.
        value
            The value to be stored.
        """
        self.instruction_count += 1
        offset, index, tag = self.parseAddress(address)
        # The ram_index indicates which addresses fall into the same block, which later help us to load the entire block into cache
        ram_index = address // self.block_size
        # Write and store to RAM
        self._ram[ram_index][address] = value
        # Write and store to Cache
        if ram_index in self._cache[index]:
            self.w_hit += 1  
            # An OrderedDict keeps the most recently inserted element at the end. By removing the cache hit block and then immediately add it back to the OrderedDict,
            # the cache hit block will remain the the end of the OrderedDict to indicate it is the most recently used.
            if self.r == 'LRU':
                item = self._cache[index].pop(ram_index)
                self._cache[index][ram_index] = item 
        else:
            self.w_miss += 1
            if len(self._cache[index]) < self.num_in_set:
                # add the entire block that contain this address
                self._cache[index][ram_index] = self._ram[ram_index]
            else:
                if self.r == 'random':
                    # pick a random key-value pair to evict
                    ram_index_list = list(self._cache[index].keys())
                    rand = random.choice(ram_index_list)
                    del self._cache[index][rand]
                else:
                    # for FIFO and LRU, evict the first element
                    self._cache[index].popitem(last = False)
                # add the new block to cache
                self._cache[index][ram_index] = self._ram[ram_index] 

    def addDouble(self, v1, v2):
        """Add 2 doubles.

        Parameters
        ----------
        v1
            A double.
        v2
            A double.

        Returns
        -------
        double
            Result of the addition.
        """
        self.instruction_count += 1
        return v1+v2

    def multDouble(self, v1,v2):
        """Multiply 2 doubles.

        Parameters
        ----------
        v1
            A double.
        v2
            A double.

        Returns
        -------
        double
            Result of the multiplication.
        """
        self.instruction_count += 1
        return v1*v2

    def print(self):
        """
        Print all parameters of the CPU, total instruction counts and cache hits/misses.
        """
        params = {
            'Ram Size': self.ram_size,
            'Cache Size': self.cache_size,
            'Block Size': self.block_size,
            'Total Blocks in Cache': self.cache_sets * self.num_in_set,
            'Associativity': self.num_in_set,
            'Number of Sets': self.cache_sets,
            'Replacement Policy': self.r,
            'Algorithm': self.a,
            'MXM Blocking Factor': self.f,
            'Matrix or Vector dimension': self.d,
        }
        results = {
            'Instruction count': self.instruction_count,
            'Read hits': self.r_hit,
            'Read misses': self.r_miss,
            'Read miss rate': (self.r_miss / (self.r_hit + self.r_miss))*100,
            'Write hits': self.w_hit,
            'Write misses': self.w_miss,
            'Write miss rate':  (self.w_miss / (self.w_hit + self.w_miss))*100
        }

        print('INPUTS', 20 * '=')
        for k, v in params.items():
            print(f'{k} = {v}')

        print('RESULTS', 20 * '=')
        for k, v in results.items():
            print(f'{k} = {v}')

'''
Argument Parsing
'''
def parseArgs():
    parser = argparse.ArgumentParser('Cache simulator')
    parser.add_argument('-c',
                        type=int,
                        default=65536, 
                        help='The size of the cache in bytes (default: 65,536)')
    parser.add_argument('-b', 
                        type=int, 
                        default=64, 
                        help='The size of a data block in bytes (default: 64)')
    parser.add_argument('-n', 
                        type=int, 
                        default=2, 
                        help='The n-way associativity of the cache. -n 1 is a direct-mapped cache. (default: 2)')
    parser.add_argument('-r', 
                        type=str, 
                        choices=['random', 'FIFO', 'LRU'], 
                        default='LRU', 
                        help='The replacement policy. Can be random, FIFO, or LRU. (default: LRU)')
    parser.add_argument('-a',
                        type=str,
                        choices=['daxpy', 'mxm', 'mxm_block'],
                        default='mxm_block',
                        help=' The algorithm to simulate (default: mxm block)')
    parser.add_argument('-d', 
                        type=int, 
                        default=480, 
                        help='The dimension of the algorithmic matrix (or vector) operation. \
                             -d 100 would result in a 100 × 100 matrix-matrix multiplication. (default: 480)')
    parser.add_argument('-p', 
                        action='store_true', 
                        default=False, 
                        help='Enables printing of the resulting “solution” matrix product or daxpy vector after the emulation is complete')
    parser.add_argument('-f', 
                        type=int, 
                        default=32, 
                        help='The blocking factor for use when using the blocked matrix multiplication algorithm. (default: 32)')
    args = parser.parse_args()

    return args

'''
Main function
'''
def main(args):
    if args.a == 'daxpy':
        # Space for 3 arguments (2 of which are vectors and one is a constant) and the output vector
        ram_size = (args.d * 3 + 1) * WORD_SIZE
        myCPU = CPU(c=args.c, b=args.b, n=args.n, r=args.r, a=args.a, d=args.d, f=args.f, ram_size=ram_size)
        d = args.d
        p = args.p
        daxpy(myCPU, d, p, WORD_SIZE)
    elif args.a == 'mxm':
        # Space for 2 arguments and 1 result (hence 3)
        ram_size = args.d * args.d * 3 * WORD_SIZE
        myCPU = CPU(c=args.c, b=args.b, n=args.n, r=args.r, a=args.a, d=args.d, f=args.f, ram_size=ram_size)
        d = args.d
        p = args.p
        mxm(myCPU, d, p,WORD_SIZE)
    else:
        # Space for 2 arguments and 1 result (hence 3)
        ram_size = args.d * args.d * 3 * WORD_SIZE
        myCPU = CPU(c=args.c, b=args.b, n=args.n, r=args.r, a=args.a, d=args.d, f=args.f, ram_size=ram_size)
        d = args.d
        f = args.f
        p = args.p
        mxm_blocked(myCPU, d, f, p, WORD_SIZE)

    
if __name__ == '__main__':
    main(args=parseArgs())
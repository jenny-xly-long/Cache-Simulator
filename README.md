# Project 1 Cache Simulator
## Jenny Long
This project aims to simulate how and L1 cache works using Python 3. We measure the cache performance with customizable configuration using 3 algorithms:
1. Daxpy (D*a + b, where a, b are vectors)
2. MxM (A * B, where A, B are square matrices)
3. MxM Block (A * B, where A, B are square matrices and we used tiled algorithm)

## Ram Implementation
The ram is implemented as a defaultdict of dict. 

We first calculate a *ram_index* where *ram_index = address / block_size*. This allows us to know which addresses fall into the same block, since all addresses with the same ram_index are in the same data block. We can think of what I call *ram_index* the combination of the tag and index bits by shifting to the right and removed all offset bits.

The *ram_index* serves as the key for the outer defaultdict. Its corresponding value is a dict of address-double pairs that fall into the same data block denoted with *ram_index*.

## Cache Implementation
The cache is implemented as an OrderedDict of OrderedDict of dict.

The key of the outer-most OrderedDict is the cache index. This ensures that all data blocks with the same cache index gets mapped to its corresponding cache block. Its corresponding value is another OrderedDict.

The key of the inner OrderedDict is *ram_index*, which indicates which data block is in the cache line. Its corresponding value is a dict of address-double pairs just like in the ram implementation.

This implementation makes loading a block of data from ram to cache very easy. The reason behind using an OrderedDict is to facilitate the LRU and FIFO replacement policies since OrderedDict keeps track of inserting orders.

## Cache Configuration
1. -c: Cache size
2. -b: Block size
3. -n: n-way associative
4. -r: Replacement policy 
5. -a: Algorithm
6. -d: Matrix/vector dimension
7. -f: Blocking factor in tiled matrix multiplication
8. -p: Print input and result matrices/vectors (if you want to see the printed results, add -p flag without any following arguments)

## Run the simulator
1. Download the repo
2. ```python3 ./cache-sim``` for default configuration
3. ```python3 ./cache-sim -c 4096 -b 8 -n 1 -r random -a daxpy -d 9``` example of customized configuration


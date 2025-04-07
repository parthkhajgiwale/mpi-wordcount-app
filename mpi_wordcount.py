from mpi4py import MPI
import json
import os

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

file_path = 'uploads/input.txt'

if rank == 0:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read()
    chunk_size = len(data) // size
    chunks = [data[i*chunk_size : (i+1)*chunk_size] for i in range(size)]
    chunks[-1] += data[size*chunk_size:]
else:
    chunks = None

chunk = comm.scatter(chunks, root=0)

local_count = len(chunk.split())

word_counts = comm.gather(local_count, root=0)

if rank == 0:
    total_words = sum(word_counts)
    with open('output.json', 'w') as f:
        json.dump({'total_words': total_words}, f)

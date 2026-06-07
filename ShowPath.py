import numpy as np
from tool import visualize_path

def GetArray():
    with open('temp.bin', 'rb') as f:
        length = np.fromfile(f, dtype=np.int32, count=1)[0]
        arr = np.fromfile(f, dtype=np.int32, count=length).tolist()
    return arr

def GetSubArray(arr):
    length = len(arr)
    result = []
    for i in range(length - 1):
        result.append((arr[i], arr[i+1]))
    
    return result

if __name__ == '__main__':
    arr = GetArray()   
    res = GetSubArray(arr)
    visualize_path("graph_data.json", res)
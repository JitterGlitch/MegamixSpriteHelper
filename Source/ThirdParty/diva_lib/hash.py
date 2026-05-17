import struct
from typing import Optional

def murmur_hash_calculate(data: bytes) -> int:
    m = 0x7FD652AD
    r = 16
    
    hash_val = 0xDEADBEEF
    length = len(data)
    index = 0
    
    while length >= 4:
        chunk = struct.unpack_from('<I', data, index)[0]
        hash_val = (hash_val + chunk) & 0xFFFFFFFF
        hash_val = (hash_val * m) & 0xFFFFFFFF
        hash_val ^= hash_val >> r
        index += 4
        length -= 4
    
    if length > 0:
        remaining = 0
        if length >= 3:
            remaining |= data[index + 2] << 16
        if length >= 2:
            remaining |= data[index + 1] << 8
        if length >= 1:
            remaining |= data[index]
        
        hash_val = (hash_val + remaining) & 0xFFFFFFFF
        hash_val = (hash_val * m) & 0xFFFFFFFF
        hash_val ^= hash_val >> r
    
    hash_val = (hash_val * m) & 0xFFFFFFFF
    hash_val ^= hash_val >> 10
    hash_val = (hash_val * m) & 0xFFFFFFFF
    hash_val ^= hash_val >> 17
    
    return hash_val

def murmur_hash_calculate_str(value: Optional[str], encoding: str = 'utf-8') -> int:
    if value is None:
        value = ""
    
    upper_value = value.upper()
    data = upper_value.encode(encoding)
    
    return murmur_hash_calculate(data)


Calculate = murmur_hash_calculate
CalculateStr = murmur_hash_calculate_str

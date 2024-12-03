import random
import string

def generate_random_id(length=26):
    """Menghasilkan ID acak dengan panjang tertentu"""
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(characters) for _ in range(length))

def generate_random_cpu_info():
    """Menghasilkan informasi CPU acak"""
    cpu_models = [
        "AMD Ryzen 5 5600G with Radeon Graphics",
        "Intel Core i7-9700K",
        "AMD Ryzen 7 5800X", 
        "Intel Core i9-10900K",
        "Intel Core i5-11600K",
        "AMD Ryzen 9 5900X",
        "Intel Core i7-12700K",
        "AMD Ryzen 5 3600X",
        "Intel Core i9-11900K",
        "AMD Ryzen 3 3200G",
        "Intel Core i9-13900K",
        "AMD Ryzen 9 7950X",
        "Intel Core i5-13600K",
        "AMD Ryzen 7 7700X",
        "Intel Core i7-13700K"
    ]

    features = ["mmx", "sse", "sse2", "sse3", "ssse3", "sse4_1", "sse4_2", "avx", "avx2", "fma3", "rdrand"]
    num_of_processors = random.choice([4, 8, 12, 16, 24, 32])

    processors = []
    for _ in range(num_of_processors):
        processors.append({
            "usage": {
                "idle": random.randint(0, 2000000000000),
                "kernel": random.randint(0, 10000000000),
                "total": random.randint(0, 2000000000000),
                "user": random.randint(0, 50000000000)
            }
        })

    return {
        "archName": random.choice(["x86_64", "amd64"]),
        "features": random.sample(features, random.randint(5, len(features))),
        "modelName": random.choice(cpu_models),
        "numOfProcessors": num_of_processors,
        "processors": processors,
        "temperatures": []
    }

def generate_random_gpu_info():
    """Menghasilkan informasi GPU acak"""
    renderers = [
        "ANGLE (AMD, AMD Radeon(TM) Graphics (0x00001638) Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "ANGLE (NVIDIA, GeForce GTX 1080 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "ANGLE (Intel, Iris Xe Graphics (0x00008086) Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "ANGLE (NVIDIA, GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "ANGLE (AMD, Radeon RX 6800 XT Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "ANGLE (NVIDIA, GeForce RTX 4090 Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "ANGLE (Intel, Arc A770 Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)"
    ]
    vendors = ["Google Inc. (AMD)", "NVIDIA", "Intel", "AMD"]
    
    return {
        "renderer": random.choice(renderers),
        "vendor": random.choice(vendors)
    }

def generate_random_operating_system():
    """Menghasilkan sistem operasi Windows acak"""
    os_list = [
        "Windows 11", "Windows 10", "Windows 8", "Windows 7"
    ]
    return random.choice(os_list)

def generate_random_system_data():
    """Menghasilkan data sistem acak lengkap"""
    return {
        "id": generate_random_id(),
        "type": "system_info",
        "data": {
            "version": "0.1.7",
            "status": "active",
            "systemInfo": {
                "gpuInfo": {
                    "renderer": generate_random_gpu_info()["renderer"],
                    "vendor": generate_random_gpu_info()["vendor"]
                },
                "memoryInfo": {
                    "availableCapacity": random.randint(4000000000, 8000000000),
                    "capacity": random.randint(8000000000, 16000000000)
                },
                "operatingSystem": generate_random_operating_system(),
                "machineId": generate_random_id(32).lower(),
                "cpuInfo": {
                    "modelName": generate_random_cpu_info()["modelName"],
                    "numOfProcessors": generate_random_cpu_info()["numOfProcessors"],
                    "processors": generate_random_cpu_info()["processors"],
                    "features": generate_random_cpu_info()["features"],
                    "archName": generate_random_cpu_info()["archName"]
                }
            }
        }
    }

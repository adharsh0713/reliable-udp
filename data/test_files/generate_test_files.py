# generate_test_files.py

sizes = {
    "small.txt": 10 * 1024,
    "medium.txt": 1024 * 1024,
    "large.txt": 10 * 1024 * 1024
}


for name, size in sizes.items():

    with open(
        f"data/test_files/{name}",
        "w"
    ) as file:

        file.write(
            "Reliable UDP experiment data\n" * 
            (size // 30)
        )
import toml

data = toml.load("pyproject.toml")
# Modify field
data["project"]["name"] = "prowler"
#data["tool"]["setuptools"]["py-modules"]  = []

# To use the dump function, you need to open the file in 'write' mode
f = open("pyproject.toml", "w")
toml.dump(data, f)
f.close()

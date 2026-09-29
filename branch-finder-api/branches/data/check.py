import json, sys
d = json.load(open(sys.argv[1]))
print("features:", len(d["features"]))
print("properties:", d["features"][0]["properties"])
print("geometry:", d["features"][0]["geometry"]["type"])

f = open("./data/stage2_groundtruths/1st_candidate_bugs.csv", "r", encoding="utf8")
lines = f.readlines()
print(len(lines))

lines = set(lines)
print(len(lines))


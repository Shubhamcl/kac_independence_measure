from numpy import loadtxt
import numpy as np
from scipy.stats import wilcoxon


#acc_reg = loadtxt("./7result_True_0.1.txt", comments="#", delimiter=",", unpack=False)


#acc_reg = loadtxt("./8result_kb_True_0.1.txt", comments="#", delimiter=",", unpack=False)
#acc = loadtxt("./8result_kb_False_0.1.txt", comments="#", delimiter=",", unpack=False)

#acc_reg = loadtxt("./10result_kb_True_0.1.txt", comments="#", delimiter=",", unpack=False)
#acc = loadtxt("./10result_kb_False_0.1.txt", comments="#", delimiter=",", unpack=False)

#acc_reg = loadtxt("./14result_chest_True_0.15.txt", comments="#", delimiter=",", unpack=False)


#acc_reg = loadtxt("./18result_chest_True_9.0.txt", comments="#", delimiter=",", unpack=False)
#acc = loadtxt("./18result_chest_False_9.0.txt", comments="#", delimiter=",", unpack=False)

#acc_reg = loadtxt("./21aresult_chest_True_0.2.txt", comments="#", delimiter=",", unpack=False) # ok
#acc = loadtxt("./backup/21result_chest_False_0.2.txt", comments="#", delimiter=",", unpack=False)


#acc_reg = loadtxt("aaa_22result_chest_True_0.15.txt", comments="#", delimiter=",", unpack=False)
#acc = loadtxt("aaa_22result_chest_False_0.15.txt", comments="#", delimiter=",", unpack=False)

acc_reg = loadtxt("./melanoma1_True_0.05.txt", comments="#", delimiter=",", unpack=False)
acc = loadtxt("./melanoma1_False_9.0.txt", comments="#", delimiter=",", unpack=False)

#acc = 0 #loadtxt("./melanmom_4_result_False_0.15.txt", comments="#", delimiter=",", unpack=False)

print("acc_reg {}, acc {}".format(np.mean(acc_reg), np.mean(acc)))
n = np.min([len(acc_reg), len(acc)])
#print("acc_reg {}, acc {}".format(np.mean(acc_reg[:n]), np.mean(acc[:n])))

print("acc_reg {}, acc {}".format(len(acc_reg), len(acc)))
#print(len(acc))
print(n)
d = acc_reg[:n] - acc[:n]
print("acc_reg")
print(acc_reg)
print("acc")
print(acc)
w, p = wilcoxon(acc_reg[:n], acc[:n], alternative="greater")
print("w, p = {} {}".format(w,p))
breakpoint()
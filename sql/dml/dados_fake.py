import pandas as pd
import numpy as np
import random
from collections import Counter

qtd_fornecedores = 200
meses = 24
tx_anomalia_mes = 0.06
seed = 42

random.seed(seed)
np.random.seed(seed)

gp_crescente = ['crescente'] * 80
gp_decrescente = ['decrescente'] * 60
gp_estavel = ['estavel'] * 60

grupos = gp_crescente + gp_decrescente + gp_estavel
random.shuffle(grupos)

Counter(grupos)

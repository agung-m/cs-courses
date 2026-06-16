import time
import numpy as np
from atomicx import AtomicInt
from reliability.Distributions import Weibull_Distribution, Exponential_Distribution, Lognormal_Distribution, Normal_Distribution

from fastapi import FastAPI

# Service fault simulator
# (c) 2026, Mulya Agung (agung@itsb.ac.id)

app = FastAPI()

RAND_SEED = 42
MAX_WORK_TIME = 1
WORK_TIME = 0.1   # Service response time in seconds
NUM_TRIALS = 1000

# Initialize the random number generator
rg = np.random.default_rng(RAND_SEED)

def apply_hazard(rg, prob):
    flips = rg.choice([False, True], size=1, p=[1-prob, prob])
    return flips[0]

def do_simulation(ctr: AtomicInt, samples: np.ndarray, label: str):
    trial_id = ctr.inc() % NUM_TRIALS
    prob = samples[trial_id]
    fail_occur = apply_hazard(rg, prob)
    print(trial_id, prob, fail_occur)

    if fail_occur:
        return {"message": "FAIL SVC-{}".format(label)}
    else:
        time.sleep(WORK_TIME)
        return {"message": "SUCCESS SVC-{}".format(label)}

# Generate samples
x_vals = np.linspace(0, NUM_TRIALS, NUM_TRIALS)
infant_mortality = Weibull_Distribution(alpha=1, beta=0.6).HF(xvals=x_vals, show_plot=False)
infant_mortality = np.nan_to_num(infant_mortality, posinf=1.0, neginf=0.0)
random_failures = Exponential_Distribution(Lambda=0.02).HF(xvals=x_vals, show_plot=False)
wear_out = Lognormal_Distribution(mu=6.8, sigma=0.012).HF(xvals=x_vals, show_plot=False)
combined = infant_mortality+random_failures+wear_out
combined = np.clip(combined, a_min=0, a_max=1)
fatigue = Normal_Distribution(0, 45).HF(xvals=x_vals, show_plot=False)

# Save the samples
np.savetxt("svc_1.samples", infant_mortality, delimiter=",", fmt="%f")
np.savetxt("svc_2.samples", random_failures, delimiter=",", fmt="%f")
np.savetxt("svc_3.samples", wear_out, delimiter=",", fmt="%f")
np.savetxt("svc_4.samples", combined, delimiter=",", fmt="%f")
np.savetxt("svc_5.samples", fatigue, delimiter=",", fmt="%f")

# Counters
svc_1_ctr = AtomicInt(0)
svc_2_ctr = AtomicInt(0)
svc_3_ctr = AtomicInt(0)
svc_4_ctr = AtomicInt(0)
svc_5_ctr = AtomicInt(0)

# Access URL: http://127.0.0.1:8000/svc-1
@app.get("/svc-1")
async def svc_1():
    global svc_1_ctr, infant_mortality
    return do_simulation(svc_1_ctr, infant_mortality, "1")

@app.get("/svc-2")
async def svc_2():
    global svc_2_ctr, random_failures
    return do_simulation(svc_2_ctr, random_failures, "2")

@app.get("/svc-3")
async def svc_3():
    global svc_3_ctr, wear_out
    return do_simulation(svc_3_ctr, wear_out, "3")

@app.get("/svc-4")
async def svc_4():
    global svc_4_ctr, combined
    return do_simulation(svc_4_ctr, combined, "4")

@app.get("/svc-5")
async def svc_5():
    global svc_5_ctr, fatigue
    return do_simulation(svc_5_ctr, fatigue, "5")

@app.get("/reset")
async def sim_reset():
    global svc_1_ctr, svc_2_ctr, svc_3_ctr, svc_4_ctr, svc_5_ctr
    svc_1_ctr.store(0)
    svc_2_ctr.store(0)
    svc_3_ctr.store(0)
    svc_4_ctr.store(0)
    svc_5_ctr.store(0)
    return {"message": "RESET"}
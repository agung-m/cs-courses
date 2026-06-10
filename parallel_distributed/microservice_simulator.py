import random
import time
import numpy as np
import scipy.stats as stats

from fastapi import FastAPI
from atomicx import AtomicInt

app = FastAPI()

rand_seed = 42
work_rg = [random.Random(seed) for seed in range(7)]
max_work_time = 5
max_samples = 1000

rg = np.random.default_rng(rand_seed)

# WEIBULL
samples_under = rg.weibull(0.5, size=max_samples)
u_min, u_max = samples_under.min(), samples_under.max()
samples_u_scaled = (samples_under - u_min) / (u_max - u_min + 1e-9)
u_list = list()
u_last_occur = AtomicInt(0)

samples_one = rg.weibull(1, size=max_samples)
o_min, o_max = samples_one.min(), samples_one.max()
samples_o_scaled = (samples_one - o_min) / (o_max - o_min + 1e-9)
o_list = list()
o_last_occur = AtomicInt(0)

samples_above = rg.weibull(1.5, size=max_samples)
a_min, a_max = samples_above.min(), samples_above.max()
samples_a_scaled = (samples_above - a_min) / (a_max - a_min + 1e-9)
a_list = list()
a_last_occur = AtomicInt(0)

# EXPONENTIAL
# Define your failure rate (e.g., 0.05 failures per day)
#failure_rate = 0.05
# INCORRECT: np.random.exponential(failure_rate)
# CORRECT: Calculate the scale (Mean Time To Failure = 20 days)
#mttf_scale = 1 / failure_rate
# Use the recommended modern Generator API
#exp_failure_times = rg.exponential(scale=mttf_scale, size=max_samples)
def_fail_rate = 0.05
exp_list = list()

# LOGNORMAL
# Parameters for the underlying normal distribution of the log-failures
mu = 2.5       # Mean of the log times
sigma = 0.4    # Standard deviation of the log times
# Generate 10000 random failure times (in hours)
# NOTE: np.random.lognormal is equivalent to np.exp(np.random.normal(mu, sigma))
lognorm_times = np.random.lognormal(mu, sigma, size=max_samples)
lognorm_cdf = stats.lognorm.cdf(lognorm_times, s=sigma, scale=np.exp(mu))
lognorm_list = list()
lognorm_last_occur = AtomicInt(0)

# POISSON
lam = 3.0
samples = rg.poisson(lam=lam, size=max_samples)
poison_cdf_vals = stats.poisson.cdf(samples, mu=lam)
poisson_list = list()
poisson_last_occur = AtomicInt(0)

# http://127.0.0.1:8000/svc-norm?fail_rate=0.05
@app.get("/svc-norm")
async def svc_norm(fail_rate: float = def_fail_rate):
    global work_rg, max_work_time, rg

    if rg.random() < fail_rate:
        return {"message": "FAIL SVC-NORM"}

    work_time = work_rg[0].randint(1, max_work_time)
    time.sleep(work_time)

    return {"message": "SUCCESS SVC-NORM - " + str(work_time)}


# http://127.0.0.1:8000/svc-binom?fail_rate=0.05
@app.get("/svc-binom")
async def svc_binom(fail_rate: float = def_fail_rate):
    global work_rg, max_work_time, rg

    if rg.binomial(1, fail_rate) == 1:
        return {"message": "FAIL SVC-BINOM"}

    work_time = work_rg[1].randint(1, max_work_time)
    time.sleep(work_time)
    return {"message": "SUCCESS SVC-BINOM - " + str(work_time)}

# http://127.0.0.1:8000/svc-expon?fail_rate=0.05
# @app.get("/svc-expon")
# async def svc_expon(fail_rate: float | float = def_fail_rate):
#     global work_rg, max_work_time, rg, exp_fail_rate, exp_list
#
#     t = len(exp_list)
#     prob_failure = 1 - np.exp(-fail_rate * t)
#     print(prob_failure)
#
#     exp_list.append(None)
#     if prob_failure < fail_rate:
#         return {"message": "FAIL SVC-EXPON"}
#
#     work_time = work_rg[5].randint(1, max_work_time)
#     time.sleep(work_time)
#     return {"message": "SUCCESS SVC-EXPON - " + str(work_time)}

# Weibull Distribution:
# Use Case: Models systems where the failure rate changes over time, commonly used for mechanical drives, aging servers, or software-induced bugs.
# Core Characteristic: Uses a shape parameter (k or β).
# If k < 1, failures decrease over time (early-life "infant mortality").
# If k = 1, failures are constant (exponential).
# If k > 1, failures increase over time (wear-out)

@app.get("/svc-weibull-1")
async def svc_weibull_1():
    global work_rg, max_work_time, rg, samples_u_scaled, u_list, u_last_occur

    t = len(u_list)
    current_fail_dist = sum(samples_u_scaled[u_last_occur.load():t])
    print(current_fail_dist)

    u_list.append(None)
    if current_fail_dist >= 1:
        u_last_occur.store(t)
        return {"message": "FAIL SVC-WEIBULL-1"}

    work_time = work_rg[2].randint(1, max_work_time)
    time.sleep(work_time)
    return {"message": "SUCCESS SVC-WEIBULL-1 - " + str(work_time)}

@app.get("/svc-weibull-2")
async def svc_weibull_2():
    global work_rg, max_work_time, rg, samples_o_scaled, o_list, o_last_occur

    #print(samples_o_scaled[len(o_list)])
    t = len(o_list)
    current_fail_dist = sum(samples_o_scaled[o_last_occur.load():t])

    o_list.append(None)
    #if samples_o_scaled[len(o_list)] > fail_rate:
    if current_fail_dist >= 1:
        o_last_occur.store(t)
        return {"message": "FAIL SVC-WEIBULL-2"}

    work_time = work_rg[3].randint(1, max_work_time)
    time.sleep(work_time)
    return {"message": "SUCCESS SVC-WEIBULL-2 - " + str(work_time)}


@app.get("/svc-weibull-3")
async def svc_weibull_3():
    global work_rg, max_work_time, rg, samples_a_scaled, a_list, a_last_occur

    t = len(a_list)
    current_fail_dist = sum(samples_a_scaled[a_last_occur.load():t])
    #print(samples_a_scaled[len(a_list)], fail_rate, current_fail_dist)

    a_list.append(None)
    #if samples_a_scaled[len(a_list)] > fail_rate:
    if  current_fail_dist >= 1:
        a_last_occur.store(t)
        return {"message": "FAIL SVC-WEIBULL-3"}

    work_time = work_rg[4].randint(1, max_work_time)
    time.sleep(work_time)
    a_list.append(None)
    return {"message": "SUCCESS SVC-WEIBULL-3 - " + str(work_time)}

# Lognormal Distribution:Use Case: Highly effective at modeling repair times (Mean Time To Repair - MTTR) in computer networks and server systems.
# Core Characteristic: Represents situations where most repairs are brief and routine, but a few complex failures take an exponentially longer time to fix.
@app.get("/svc-lognorm")
async def svc_lognorm():
    global work_rg, max_work_time, rg, lognorm_list, lognorm_cdf, lognorm_last_occur

    t = len(lognorm_list)
    cdf = sum(lognorm_cdf[lognorm_last_occur.load():t])
    #print(cdf)

    lognorm_list.append(None)
    if cdf >= 1:
        lognorm_last_occur.store(t)
        return {"message": "FAIL SVC-LOGNORM"}

    work_time = work_rg[5].randint(1, max_work_time)
    time.sleep(work_time)
    return {"message": "SUCCESS SVC-LOGNORM - " + str(work_time)}

# Poisson Distribution:Use Case: Models the number of independent failures that occur within a fixed interval of time or space.
# Core Characteristic: Useful for calculating the probability of experiencing a specific number of discrete failures (e.g., exactly 3 disk crashes in a month)
@app.get("/svc-poisson")
async def svc_poisson():
    global work_rg, max_work_time, rg, poisson_list, poison_cdf_vals, poisson_last_occur

    t = len(poisson_list)
    cdf = sum(poison_cdf_vals[poisson_last_occur.load():t])
    print(cdf)

    poisson_list.append(None)
    if cdf >= 1:
        poisson_last_occur.store(t)
        return {"message": "FAIL SVC-POISSON"}

    work_time = work_rg[6].randint(1, max_work_time)
    time.sleep(work_time)
    return {"message": "SUCCESS SVC-POISSON - " + str(work_time)}
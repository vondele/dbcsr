#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from glob import glob
import re
import json
from ast import literal_eval
from kernels.cusmm_dnt import kernel_algorithm

re_mnk    = re.compile(r"tune_(\d+)x(\d+)x(\d+)_")
re_winner = re.compile(r"\nWINNER: \d+ (.+)\n")
re_gflops = re.compile(r"# ([0-9.]+) GFlop/s")
re_errors = re.compile(r"Number of errors: (\d+)\n")
re_kernel_descr = re.compile(r"Kernel_dnt_(\w+)(\(.*\)) , # (\d+\.\d+) GFlop/s")

def get_kernel(kernel_descr):
    match = re_kernel_descr.search(kernel_descr).groups()
    algo = match[0]
    m = match[1].replace('=', '\':')
    m = m.replace(', ', ', \'')
    m = m.replace('(', '{\'')
    m = m.replace(')', '}')
    params = dict(literal_eval(m))
    params['perf'] = match[2]
    return kernel_algorithm[algo](**params)

#===============================================================================
def main():
    winners = dict()

    for d in glob("tune_*"):
        if not os.path.isdir(d):
            continue

        for exe_fn in glob(d+"/tune_*main.cu"):
            mnk = tuple([int(i) for i in re_mnk.search(exe_fn).groups()])
            log_fn = exe_fn.replace("_main.cu", ".log")
            if not os.path.exists(log_fn):
                winners[mnk] = "log missing: "+log_fn
                continue

            process_log(log_fn, mnk, winners)

    # Get kernel objects from list of strings
    kernels = [get_kernel(kernel_descr) for kernel_descr in winners.values()]
    with open("parameters.txt", 'w') as f:
        s = json.dumps([kernel.as_dict for kernel in kernels])
        s = s.replace('}, ', '},\n')
        s = s.replace('[', '[\n')
        s = s.replace(']', '\n]')
        f.write(s)

    print("Wrote parameters.txt")

#===============================================================================
def process_log(log_fn, mnk, winners):
    print("Reading: "+log_fn)

    f = open(log_fn)
    content = f.read()
    f.close()

    m = re_errors.search(content)
    if not m:
        winners[mnk] = "log incomplete: "+log_fn
        return

    n_errors = int(m.group(1))
    if n_errors != 0:
        winners[mnk] = "errors: "+log_fn
        return

    old_gflops = 0.0
    if mnk in winners.keys():
        m = re_gflops.search(winners[mnk])
        if not m:
            return
        old_gflops = float(m.group(1))

    new_winner = re_winner.search(content).group(1).strip().replace("GFlops","GFlop/s")
    new_gflops = float(re_gflops.search(new_winner).group(1))

    if new_gflops > old_gflops :
        winners[mnk] = new_winner


#===============================================================================
if len(sys.argv)==2 and sys.argv[-1]=="--selftest":
    pass #TODO implement selftest
else:
    main()

#EOF

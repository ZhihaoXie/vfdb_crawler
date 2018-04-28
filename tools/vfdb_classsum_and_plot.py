#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# FileName:  vfdb_classsum_and_plot.py
# Author:    Zhihao Xie  \(#^o^)/
# Date:      2018/1/26 14:07
# Version:   v1.0.0
# CopyRight: Copyright ©Zhihao Xie, All rights reserved.

# Note: summary of vfs blastout and pie plot

import sys, re, os
from collections import OrderedDict
import matplotlib.pyplot as plt

def draw_pie(profix_file, out_prefix):
    vfs_dict = OrderedDict()
    with open(profix_file) as fh:
        for line in fh:
            if re.search(r"^Level1", line):
                continue
            fields = line.strip().split('\t')
            vfs_dict.setdefault(fields[0], {})
            vfs_dict[fields[0]][fields[1]] = int(fields[2])

    fig = plt.figure(figsize=(12, 10))
    num = 1
    for k1 in vfs_dict:
        if k1 == "Others":
            continue
        vitems = vfs_dict[k1].items()
        ph_names, ph_values = zip(*vitems)
        p1 = fig.add_subplot(2, 2, num)
        patches, texts, autotexts = p1.pie(ph_values, labels=ph_names, labeldistance=1.1, autopct='%3.1f%%', startangle=90, pctdistance=0.65)
        # set text
        for idx in range(len(autotexts)):
            autotexts[idx].set_text(ph_values[idx])
        # p1.text(-0.65, 1.3, k1, fontsize=12)
        p1.set_title(k1, fontsize=12, color='black')
        p1.legend(fontsize=7, loc='right', bbox_to_anchor=(1.28, 0.2))
        num += 1

    fig.savefig(out_prefix+".vf_pieplot.pdf")
    fig.savefig(out_prefix+'.vf_pieplot.png')

def main():
    if len(sys.argv) < 3:
        print("python3 %s <vf_bsp_out> <out_prefix>" % sys.argv[0])
        sys.exit(1)

    # VFDB_level_table = "/sdd/database/VFDB/VFDB_level_gene_link.txt"
    selfscript_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    VFDB_level_table = os.path.join(selfscript_path, "..", "vfdb_info", "VFDB_level_gene_link.txt")
    if not os.path.isfile(VFDB_level_table):
        print("Error: %s don't exist.")
        sys.exit(1)

    symbol2level = {}
    gene2symbol = {}
    with open(VFDB_level_table) as fh:
        for line in fh:
            if re.match(r'Level1', line):
                continue
            fields = line.strip().split("\t")
            if fields[3] == '-' or fields[3] == "":
                continue
            symbol2level.setdefault(fields[3], set()).add("\t".join(fields[:2]))
            gene_list = re.split(r',\s*', fields[4])
            for gene in gene_list:
                if gene != "" or gene != '-':
                    gene2symbol[gene] = fields[3]

    level_sum_dict = OrderedDict()
    with open(sys.argv[1]) as fh:
        for line in fh:
            if re.search(r'^Query|^\s*$', line):
                continue
            fields = line.strip().split("\t")
            vfid = fields[2]
            vf_symbol = fields[11]
            if vf_symbol in symbol2level:
                for level in sorted(list(symbol2level[vf_symbol])):
                    level_sum_dict.setdefault(level, 0)
                    level_sum_dict[level] += 1
            elif vfid in gene2symbol:
                tmp_symbol = gene2symbol[vfid]
                if tmp_symbol in symbol2level:
                    for level in sorted(list(symbol2level[vf_symbol])):
                        level_sum_dict.setdefault(level, 0)
                        level_sum_dict[level] += 1
            else:
                level_sum_dict.setdefault('Others\tOthers', 0)
                level_sum_dict['Others\tOthers'] += 1

    out_prefix = sys.argv[2]
    with open(out_prefix+".vf_sum.txt", 'w') as outfh:
        outfh.write("Level1\tLevel2\tNumber\n")
        for level in sorted(level_sum_dict.keys()):
            if not re.search(r'^Others', level):
                outfh.write("%s\t%s\n" % (level, level_sum_dict[level]))
        outfh.write("Others\tOthers\t" + str(level_sum_dict['Others\tOthers']) + "\n")

    # pie plot
    sum_file = out_prefix+".vf_sum.txt"
    draw_pie(sum_file, out_prefix)

if __name__ == '__main__':
    main()


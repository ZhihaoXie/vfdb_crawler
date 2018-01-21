#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# FileName:  vfs_crawler.py
# Author:    Zhihao Xie  \(#^o^)/
# Date:      2018/1/20 10:38
# Version:   v1.0.0
# CopyRight: Copyright ©Zhihao Xie, All rights reserved.

import sys, re, os
from collections import OrderedDict
import requests
from bs4 import BeautifulSoup

def downloadHTML(url, retries=4):
    # download html from url
    print("Download:", url)
    try:
        kv = {"user-agent": "Mozilla/5.0"}
        r = requests.get(url, headers=kv, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        html = r.text
    except:
        if retries > 0:
            if 500 <= r.status_code < 600:
                return downloadHTML(url, retries-1)
    return html

def parserGeneHtml(htmlfile):
    accession, cog, cog_code, organism, product = '-', '-', '-', '-', '-'
    dna_str, protein_str = '', ''
    with open(htmlfile) as fh:
        for line in fh:
            if re.search(r"^\s*$", line):
                continue
            if re.search(r"<b>Organism:?", line):
                soup = BeautifulSoup(line, 'html.parser')
                organism = soup.a.string
                organism = str(organism).strip()
            if re.search(r"<b>Accession:?", line):
                soup = BeautifulSoup(line, 'html.parser')
                accession = soup.a.get_text()
            if re.search(r"<b>COG:?", line):
                soup = BeautifulSoup(line, 'html.parser')
                cog = soup.a.get_text()
            if re.search(r"<b>Code:?", line):
                soup = BeautifulSoup(line, 'html.parser')
                cog_code = soup.a.get_text()
            if re.search(r"<b>Product:?", line):
                soup = BeautifulSoup(line, 'html.parser')
                product = soup.get_text()
                product = re.sub(r"Product:\s*", "", product, re.I)
                product = product.strip()
            if re.search(r"<b>DNA:?", line):
                soup = BeautifulSoup(line, 'html.parser')
                dna_str = soup.textarea.get_text()
            if re.search(r"<b>Protein:", line):
                soup = BeautifulSoup(line, 'html.parser')
                protein_str = soup.textarea.get_text()
    return [accession,cog,cog_code,product,organism,dna_str,protein_str]

def main():
    url = "http://www.mgc.ac.cn/VFs/search_VFs.htm"
    #url = "http://httpstat.us/500"
    html = downloadHTML(url)
    #print(html)

    # get level1 and level2 href
    level1to2 = OrderedDict()
    level2to3 = OrderedDict()
    soup = BeautifulSoup(html, 'html.parser')
    contents = soup.p.contents
    for idx, value in enumerate(contents):
        value = str(value)
        if re.search(r'\s\d+\)\s*', value):
            match2 = re.search(r'<a\s+href="(.+)"\s*>(.+)</a>', str(contents[idx+1]), re.DOTALL)  # level2
            if match2:
                suburl = "http://www.mgc.ac.cn" + match2.group(1)
                #suburl = re.sub(r"\s+.*$", "", suburl)
                suburl = suburl.strip()
                tag_str2 = re.sub(r'\s+', ' ', match2.group(2))
                tag_str2 = tag_str2.strip()
                level1to2[level1].append([suburl, tag_str2])
                level2to3.setdefault(tag_str2, [])
        elif re.search(r'\s\d\.\d\)\s*', value):
            match3 = re.search(r'<a\s+href="(.+)"\s*>(.+)</a>', str(contents[idx + 1]), re.DOTALL)  # level3
            if match3:
                suburl = "http://www.mgc.ac.cn" + match3.group(1)
                suburl = suburl.strip()
                tag_str3 = re.sub(r'\s+', ' ', match3.group(2))
                level2to3[tag_str2].append([suburl, tag_str3])
        else:
            match1 = re.search(r'<font\s+color=.*><b>(.+)</b>', value)
            if not match1:
                match1 = re.search(r'<b><font\s+color=.*>(.+)</font></b>', value)
            if match1:
                level1 = match1.group(1)
                level1to2.setdefault(level1, [])

    #print(level1to2)
    #print(level2to3)
    #print(level2to3['Toxin'])
    gene_info_out = open("VFDB_gene_info.txt", 'w')
    gene_info_out.write("GeneID\tGene\tAccession\tCOG\tCode\tProduct\tOrganism\n")
    gene_protein_seq = open("VFDB_gene_protein.faa", 'w')
    gene_dna_seq = open("VFDB_gene_dna.ffn", 'w')

    uniq_genes = set()
    gene4vfg = OrderedDict()
    level4gene = OrderedDict()
    for k1,v1 in level1to2.items():
        for url_symbal in v1:
            suburl = url_symbal[0]
            symbal = url_symbal[1]  # level2 name
            if len(level2to3[symbal]) == 0:
                l3_symbal = '-'
                html_l2 = downloadHTML(suburl)
                soup_l2 = BeautifulSoup(html_l2, 'html.parser')
                alist = soup_l2.find_all('a')
                for tag in alist:
                    # example: <a class=a05 href="/cgi-bin/VFs/vfs.cgi?Genus=Acinetobacter&Keyword=Biofilm formation#Bap"><font title="biofilm-associated protein">Bap</font></a>
                    if re.search(r"\&Keyword=", tag['href']):
                        tag_url = "http://www.mgc.ac.cn" + tag['href']
                        #tag_string = tag.string
                        html_l2_ele = downloadHTML(tag_url)
                        soup_l2_ele = BeautifulSoup(html_l2_ele, 'html.parser')
                        ele_alist = soup_l2_ele.find_all('a')
                        for ele_tag in ele_alist:
                            # example: <a class=a04 href="/cgi-bin/VFs/gene.cgi?GeneID=VFG037705">adeF</a>
                            if 'href' in ele_tag.attrs:
                                matc1 = re.search(r'/cgi-bin/VFs/gene.cgi\?GeneID=(\w+)', ele_tag['href'])
                                if matc1:
                                    gene_id = matc1.group(1)
                                    gene_name = ele_tag.string
                                    gene4vfg.setdefault(gene_name, set()).add(gene_id)  # gene name 2 vfg id
                                    level4gene.setdefault(k1, OrderedDict()).setdefault(symbal, OrderedDict()).setdefault(l3_symbal, set()).add(gene_name)
                                    if gene_id not in uniq_genes:
                                        uniq_genes.add(gene_id)
                                        gene_url = "http://www.mgc.ac.cn" + ele_tag['href']
                                        gene_html = downloadHTML(gene_url)
                                        with open("tmp_gene_contents.html", 'w') as outfh:
                                            outfh.write(gene_html)
                                        if os.path.exists("tmp_gene_contents.html"):
                                            gene_info = parserGeneHtml("tmp_gene_contents.html")
                                            protein_seq = gene_info.pop()
                                            dna_seq = gene_info.pop()
                                            gene_info = [gene_id, gene_name] + gene_info
                                            gene_info_out.write("\t".join(gene_info) + "\n")
                                            if len(protein_seq) > 0:
                                                gene_protein_seq.write(">%s\n%s\n" % (gene_id, protein_seq))
                                            if len(dna_seq) > 0:
                                                gene_dna_seq.write(">%s\n%s\n" % (gene_id, dna_seq))
                                        else:
                                            print("Error: the gene of %s html don't exists." % gene_name)
                                    else:
                                        continue
            else:
                for tmp_list in level2to3[symbal]:
                    l3_url = tmp_list[0]
                    l3_symbal = tmp_list[1]  # level3 name
                    html_l3 = downloadHTML(l3_url)
                    soup_l3 = BeautifulSoup(html_l3, 'html.parser')
                    alist = soup_l3.find_all('a')
                    for tag in alist:
                        # example: <a class=a05 href="/cgi-bin/VFs/vfs.cgi?Genus=Acinetobacter&Keyword=Biofilm formation#Bap"><font title="biofilm-associated protein">Bap</font></a>
                        if re.search(r"\&Keyword=", tag['href']):
                            tag_url = "http://www.mgc.ac.cn" + tag['href']
                            #tag_string = tag.string
                            html_l2_ele = downloadHTML(tag_url)
                            soup_l2_ele = BeautifulSoup(html_l2_ele, 'html.parser')
                            ele_alist = soup_l2_ele.find_all('a')
                            for ele_tag in ele_alist:
                                # example: <a class=a04 href="/cgi-bin/VFs/gene.cgi?GeneID=VFG037705">adeF</a>
                                if 'href' in ele_tag.attrs:
                                    matc1 = re.search(r'/cgi-bin/VFs/gene.cgi\?GeneID=(\w+)', ele_tag['href'])
                                    if matc1:
                                        gene_id = matc1.group(1)
                                        gene_name = ele_tag.string
                                        gene4vfg.setdefault(gene_name, set()).add(gene_id)  # gene name 2 vfg id
                                        level4gene.setdefault(k1, OrderedDict()).setdefault(symbal, OrderedDict()).setdefault(
                                            l3_symbal, set()).add(gene_name)
                                        if gene_id not in uniq_genes:
                                            uniq_genes.add(gene_id)
                                            gene_url = "http://www.mgc.ac.cn" + ele_tag['href']
                                            gene_html = downloadHTML(gene_url)
                                            with open("tmp_gene_contents.html", 'w') as outfh:
                                                outfh.write(gene_html)
                                            if os.path.exists("tmp_gene_contents.html"):
                                                gene_info = parserGeneHtml("tmp_gene_contents.html")
                                                protein_seq = gene_info.pop()
                                                dna_seq = gene_info.pop()
                                                gene_info = [gene_id, gene_name] + gene_info
                                                gene_info_out.write("\t".join(gene_info) + "\n")
                                                if len(protein_seq) > 0:
                                                    gene_protein_seq.write(">%s\n%s\n" % (gene_id, protein_seq))
                                                if len(dna_seq) > 0:
                                                    gene_dna_seq.write(">%s\n%s\n" % (gene_id, dna_seq))
                                            else:
                                                print("Error: the gene of %s html don't exists." % gene_name)
                                        else:
                                            continue

    gene_info_out.close()
    gene_protein_seq.close()
    gene_dna_seq.close()

    with open("VFDB_level_gene_link.txt", 'w') as outfh2:
        # header
        outfh2.write("Level1\tLevel2\tLevel3\tGeneID\tRelatedGenes\n")
        for l1 in level4gene:
            for l2 in level4gene[l1]:
                for l3 in level4gene[l1][l2]:
                    for gname in level4gene[l1][l2][l3]:
                        vfgs = ', '.join(gene4vfg[gname])
                        outfh2.write("%s\t%s\t%s\t%s\t%s\n" % (l1,l2,l3,gname,vfgs))

    if os.path.exists("tmp_gene_contents.html"):
        os.remove("tmp_gene_contents.html")


if __name__ == '__main__':
    main()

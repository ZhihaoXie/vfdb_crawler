# vfdb_crawler
a crawler of [VFDB](http://www.mgc.ac.cn/VFs/main.htm) to get the vfs class information

# Install

git clone git@github.com:ZhihaoXie/vfdb_crawler.git

Require:

+ requests
+ BeautifulSoup4

# Output

4 files of VFDB, see the vfdb_info directory

+ VFDB_gene_dna.ffn: vfs gene dna sequences
+ VFDB_gene_protein.faa: vfs gene protein sequences
+ VFDB_gene_info.txt: information about vfs gene, include Accession, COG etc
+ VFDB_level_gene_link.txt: the vfs class information


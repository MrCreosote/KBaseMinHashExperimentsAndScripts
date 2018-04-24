# Testing Sourmash / Mash against KBase CI RefSeq

This is a very Q&D exercise in preparing KBase CI RefSeq assemblies for
searching via Sourmash and Mash. There's tons of opportunities for speeding this up.

Test bed is a laptop with 32GB memory, 7500rpm disks, and a Intel i7-3840QM quad core hyperthreaded
processor at 2.8GHz with Ubuntu 14.04 running in a VirtualBox VM with 26GB memory and 4 virtual
CPUs.

## Fetching the data set

Summarized the RefSeq workspace with `summarize_ref_assemblies.py`

Took the first 1000 records with `head -n 1000`

Add handle ids to output with ipython loop (`ws` = workspace client,
`out` = output file):

```
for l in open('ref_assemblies_ci_1000.csv'):
    l = l.strip()
    o = ws.get_objects2({'objects': [{'ref': l.split()[0]}], 'no_data': 1})
    out.write(l + ' ' + o['data'][0]['extracted_ids']['handle'][0] + '\n')
    print(o['data'][0]['extracted_ids']['handle'])
```

Note you could get the handles in `summarize_ref_assemblies.py`, although this
requires pulling the provenance data as well.

Added handle info with ipython loop (`ah` = AbstractHandle client):

```
for l in open('ref_assemblies_ci_1000_hid.csv'):
    l = l.strip()
    hl = ah.hids_to_handles([l.split()[-1]])
    if hl:
        h = hl[0]
        out.write(l + ' ' + h['id'] + ' ' + h['file_name'] + ' ' + h['remote_md5'] + '\n')
        print(h['id'])
    else:
        print('Missing handle: ' + l)
```


pulled data from shock:

```
for l in open('ref_assemblies_ci_1000_hid_shk.csv'):
    l = l.strip().split()
    upa = l[0]
    shockid = l[5]
    safe_upa = upa.replace('/', '_')
    curl_cmd = 'curl -s https://ci.kbase.us/services/shock-api/node/{}?download > kb_refseq/{}'.format(shockid, safe_upa)
    !$curl_cmd
    print(upa)
```

make files uppercase in place (Sourmash ignores lower case characters,
apparently):

```
for file in *;
do
      awk '{ if ($0 !~ />/) {print toupper($0)} else {print $0} }' "$file" > "$(basename "$file")_s";
      mv "$(basename "$file")_s" $file;
done
```

## Sketching and searching with Sourmash

Note that all the sequences were capitalized prior to sketching as Sourmash
ignores lower case signatures, and all the bacterial isolates were lower
cased. However, the euks were capitalized as well which is probably not right.
The sequences should be re-sketched after fixing the euks.

### 1000 CI Refdata sequences

```
$ date; sourmash compute -k 31 --scaled 1000 -o ../kb_refseq_ci_1000.sigs *; date
Sat Apr 14 14:50:08 PDT 2018
setting num_hashes to 0 because --scaled is set
computing signatures for files: 15792_1001_1,
*snip*
saved 1000 signature(s). Note: signature license is CC0.
Sat Apr 14 14:57:37 PDT 2018
```

```
date; sourmash index -k 31 kb_refseq_ci_1000.sbt kb_refseq_ci_1000.sigs; date
Sat Apr 14 15:01:58 PDT 2018
loading 1 files into SBT
...sig loading 999
loaded 1000 sigs; saving SBT under "kb_refseq_ci_1000.sbt"

Finished saving nodes, now saving SBT json file.
Sat Apr 14 15:03:55 PDT 2018
```

```
$ sourmash compute -k 31 --scaled 1000 -o ../kb_refseq_ci_1000_15792_446_1.sig 15792_446_1 
setting num_hashes to 0 because --scaled is set
computing signatures for files: 15792_446_1
Computing signature for ksizes: [31]
Computing only DNA (and not protein) signatures.
Computing a total of 1 signature(s).
... reading sequences from 15792_446_1
calculated 1 signatures for 405 sequences in 15792_446_1
saved 1 signature(s). Note: signature license is CC0.
```

Search with SBT
```
$ date; sourmash search kb_refseq_ci_1000_15792_446_1.sig kb_refseq_ci_1000.sbt.sbt.json; date
Sat Apr 14 15:26:11 PDT 2018
select query k=31 automatically.
loaded query: 15792_446_1... (k=31, DNA)
loaded 1 databases.

74 matches; showing first 3:
similarity   match
----------   -----
100.0%       15792_446_1
 86.4%       15792_431_1
 68.3%       15792_326_2
Sat Apr 14 15:26:57 PDT 2018
```

Search w/o SBT
```
$ date; sourmash search kb_refseq_ci_1000_15792_446_1.sig kb_refseq_ci_1000.sigs; date
Sat Apr 14 17:50:05 PDT 2018
select query k=31 automatically.
loaded query: 15792_446_1... (k=31, DNA)
...sig loading 999
loaded 1000 signatures.

74 matches; showing first 3:
similarity   match
----------   -----
100.0%       15792_446_1
 86.4%       15792_431_1
 68.3%       15792_326_2
Sat Apr 14 17:51:40 PDT 2018
```

### All CI Refdata sequences

```
date; sourmash compute -k 31 --scaled 1000 -o ../kb_refseq_ci.sigs *; date
Sat Apr 21 17:01:39 PDT 2018
setting num_hashes to 0 because --scaled is set
computing signatures for files: 15792_100001_1, 15792_

... reading sequences from 15792_99998_1
calculated 1 signatures for 24 sequences in 15792_99998_1
saved 43892 signature(s). Note: signature license is CC0.
Sun Apr 22 07:52:10 PDT 2018
```

```
date; sourmash index -k 31 kb_refseq_ci ~/kb_refseq_sourmash/kb_refseq_ci.sigs; date
Sun Apr 22 18:08:16 PDT 2018
loading 1 files into SBT
...sig loading 43,891
loaded 43892 sigs; saving SBT under "kb_refseq_ci"

Finished saving nodes, now saving SBT json file.
Mon Apr 23 01:37:44 PDT 2018
```

```
$ date; sourmash search ~/kb_refseq_sourmash/kb_refseq_ci_1000_15792_446_1.sig ~/kb_refseq_sourmash/kb_refseq_ci.sigs; date
Mon Apr 23 14:35:05 PDT 2018
select query k=31 automatically.
loaded query: 15792_446_1... (k=31, DNA)
...sig loading 43,891
loaded 43892 signatures from /home/crusherofheads/kb_refseq_sourmash/kb_refseq_cloaded 43892 signatures.

272 matches; showing first 3:
similarity   match
----------   -----
100.0%       15792_446_1
 86.4%       15792_431_1
 68.3%       15792_326_2
Mon Apr 23 21:27:08 PDT 2018
```

## Sketching and searching with Mash

Note the -s parameter is the number of hashes per assembly. For Sourmash it's the scaling
parameter.

### 1000 CI Refdata sequences
```
$ date; ~/bin/mash/mash-Linux64-v2.0/mash sketch -s 1000 -k 31 -o ../kb_refseq_ci_1000 *; date;
Wed Apr 18 13:05:55 PDT 2018
Sketching 15792_1001_1...
*snip*
Sketching 15792_998_1...
Writing to ../kb_refseq_ci_1000.msh...
Wed Apr 18 13:08:29 PDT 2018
```

```
$ date; ~/bin/mash/mash-Linux64-v2.0/mash sketch -s 1000 -k 31 -o ../kb_refseq_ci_1000_15792_446_1 15792_446_1; date;
Wed Apr 18 13:13:57 PDT 2018
Sketching 15792_446_1...
Writing to ../kb_refseq_ci_1000_15792_446_1.msh...
Wed Apr 18 13:13:57 PDT 2018
```

```
$ date; ~/bin/mash/mash-Linux64-v2.0/mash dist kb_refseq_ci_1000_15792_446_1.msh kb_refseq_ci_1000.msh; date
Wed Apr 18 13:19:34 PDT 2018
15792_446_1	15792_1001_1	1	1	0/1000
15792_446_1	15792_1004_1	1	1	0/1000
*snip*
15792_446_1	15792_440_1	0.00986267	0	583/1000
15792_446_1	15792_443_1	0.00871973	0	617/1000
15792_446_1	15792_446_1	0	0	1000/1000
15792_446_1	15792_449_1	0.00993274	0	581/1000
15792_446_1	15792_452_1	0.00938122	0	597/1000
15792_446_1	15792_455_1	0.00907983	0	606/1000
15792_446_1	15792_458_1	0.00727582	0	664/1000
15792_446_1	15792_461_1	0.00707294	0	671/1000
15792_446_1	15792_46_3	1	1	0/1000
15792_446_1	15792_464_1	0.010469	0	566/1000
15792_446_1	15792_467_1	0.00673197	0	683/1000
15792_446_1	15792_470_1	0.00911301	0	605/1000
15792_446_1	15792_473_1	0.00730504	0	663/1000
15792_446_1	15792_476_1	0.00733433	0	662/1000
15792_446_1	15792_479_1	0.00941509	0	596/1000
15792_446_1	15792_482_1	0.00944905	0	595/1000
15792_446_1	15792_485_1	0.00742257	0	659/1000
15792_446_1	15792_488_1	0.0729295	0	55/1000
15792_446_1	15792_491_1	0.0102881	0	571/1000
15792_446_1	15792_49_3	1	1	0/1000
15792_446_1	15792_494_1	0.00730504	0	663/1000
15792_446_1	15792_497_1	0.200503	4.61581e-10	1/1000
*snip*
15792_446_1	15792_545_1	0.200503	4.66299e-10	1/1000
15792_446_1	15792_548_1	0.200503	4.56773e-10	1/1000
15792_446_1	15792_551_1	1	1	0/1000
*snip*
15792_446_1	15792_998_1	1	1	0/1000
Wed Apr 18 13:19:34 PDT 2018
```

### All CI Refdata sequences
```
date; ~/bin/mash/mash-Linux64-v2.0/mash sketch -s 1000 -k 31 -o ../kb_refseq_ci *; date;
Fri Apr 20 10:48:24 PDT 2018
Sketching 15792_100001_1...
*snip*
Sketching 15792_99995_1...
Sketching 15792_99998_1...
Writing to ../kb_refseq_ci.msh...
Fri Apr 20 15:49:40 PDT 2018
```

```
$ date; ~/bin/mash/mash-Linux64-v2.0/mash dist -d .5 ~/kb_refseq_sourmash/kb_refseq_ci_1000_15792_446_1.msh kb_refseq_ci.msh; date
Fri Apr 20 16:47:26 PDT 2018
15792_446_1	15792_115033_1	0.00673197	0	683/1000
15792_446_1	15792_115039_1	0.0114459	0	540/1000
15792_446_1	15792_115045_1	0.00733433	0	662/1000
*snip*
15792_446_1	15792_440_1	0.00986267	0	583/1000
15792_446_1	15792_443_1	0.00871973	0	617/1000
15792_446_1	15792_446_1	0	0	1000/1000
15792_446_1	15792_449_1	0.00993274	0	581/1000
15792_446_1	15792_452_1	0.00938122	0	597/1000
15792_446_1	15792_455_1	0.00907983	0	606/1000
15792_446_1	15792_458_1	0.00727582	0	664/1000
15792_446_1	15792_461_1	0.00707294	0	671/1000
*snip*
15792_446_1	15792_87308_1	0.200503	4.65234e-10	1/1000
15792_446_1	15792_87312_1	0.200503	4.70679e-10	1/1000
15792_446_1	15792_87316_1	0.200503	4.69462e-10	1/1000
15792_446_1	15792_87321_1	0.200503	4.68378e-10	1/1000
15792_446_1	15792_87327_1	0.200503	4.67074e-10	1/1000
Fri Apr 20 16:47:28 PDT 2018
```

### Merging a single sketch into a sketch DB

Note that Mash does not support in-place updates - a new file is created.

```
$ date; ~/bin/mash/mash-Linux64-v2.0/mash paste mash_paste_test kb_refseq_ci.msh ~/kb_refseq_sourmash/prod/kb_refseq_prod_19217_356482_1.msh; date
Tue Apr 24 10:53:54 PDT 2018
Writing mash_paste_test.msh...
Tue Apr 24 10:53:57 PDT 2018
```

```
$ ls -lh
total 792M
drwxrwxr-x 2 crusherofheads crusherofheads 1.6M Apr 20 21:01 kb_refseq_ci
-rw-r--r-- 1 crusherofheads crusherofheads 340M Apr 20 15:49 kb_refseq_ci.msh
-rw-r--r-- 1 crusherofheads crusherofheads 101M Apr 20 15:49 kb_refseq_ci.msh.gz
-rw-rw-r-- 1 crusherofheads crusherofheads  11M Apr 23 01:37 kb_refseq_ci.sbt.json
-rw-r--r-- 1 crusherofheads crusherofheads 340M Apr 24 10:53 mash_paste_test.msh
```

# Summary

Note that Mash uses 1000 hashes per genome, while Sourmash uses scaled hashes.

|Tool     |Sequences|Sketch time|Index time|Search time       |
|---------|---------|-----------|----------|------------------|
|Sourmash |1000     |7:29       |1:57      |0:46 (vs SBT)     |
|Mash     |1000     |2:34       |n/a       |< 1s              |
|Sourmash |43892    |14:50:31   |7:29:28   |6:52:03 (w/o SBT*)|
|Mash     |43892    |5:01:16    |n/a       |2s                |

* It seems searching with an SBT is [broken](https://github.com/dib-lab/sourmash/issues/454) in
the current release, 2.0.0a4, and produces no results in 1:22:17. Searching directly against the
sketches does produce the expected results.

It takes Mash 3s to add a single sequence to a file containing 43892 sequences.

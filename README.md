# Testing Sourmash against KBase CI RefSeq

This is a very Q&D exercise in preparing 1000 KBase CI RefSeq assemblies for
searching via Sourmash. There's tons of opportunities for speeding this up.

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
